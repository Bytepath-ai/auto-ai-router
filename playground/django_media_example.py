"""
Django Media class and merge functionality example
Based on Django's forms/widgets.py implementation
"""

import warnings
from itertools import chain


class MediaOrderConflictWarning(RuntimeWarning):
    """
    Warning raised when CSS or JS files are in conflicting order.
    """
    pass


class Media:
    """
    Media class for handling CSS and JavaScript files for Django widgets.
    """
    
    def __init__(self, media=None, css=None, js=None):
        if media is not None:
            css = getattr(media, 'css', {})
            js = getattr(media, 'js', [])
        else:
            if css is None:
                css = {}
            if js is None:
                js = []
        
        self._css = css
        self._js = js
    
    def render(self):
        """Render the HTML for the media files."""
        return '\n'.join(chain(*[
            getattr(self, 'render_' + name)() for name in MEDIA_TYPES
        ]))
    
    def render_js(self):
        """Render the JavaScript includes."""
        return [
            '<script src="%s"></script>' % self.absolute_path(path)
            for path in self._js
        ]
    
    def render_css(self):
        """Render the CSS includes."""
        media = []
        for medium in self._css:
            for path in self._css[medium]:
                media.append(
                    '<link href="%s" media="%s" rel="stylesheet">' % (
                        self.absolute_path(path), medium
                    )
                )
        return media
    
    def absolute_path(self, path):
        """
        Given a relative or absolute path to a static asset, return an absolute
        path. An absolute path will be returned unchanged while a relative path
        will be passed to django.templatetags.static.static().
        """
        from django.templatetags.static import static
        from django.utils.html import conditional_escape
        
        if path.startswith(('http://', 'https://', '/')):
            return path
        return conditional_escape(static(path))
    
    def __getitem__(self, name):
        """Return a Media object that only contains media of the given type."""
        if name in MEDIA_TYPES:
            return Media(**{str(name): getattr(self, '_' + name)})
        raise KeyError('Unknown media type "%s"' % name)
    
    @property
    def _js(self):
        """
        The _js property implementation that handles merging and ordering.
        This is where MediaOrderConflictWarning would be raised.
        """
        js = self._js_lists[:]
        
        # Check for ordering conflicts
        for list1, list2 in _pairwise(js):
            # Check if there are common elements in different order
            common = set(list1) & set(list2)
            if common:
                # Check ordering
                for item in common:
                    idx1 = list1.index(item)
                    idx2 = list2.index(item)
                    
                    # Check if items before/after in list1 appear in different order in list2
                    items_before_1 = set(list1[:idx1])
                    items_after_1 = set(list1[idx1+1:])
                    
                    for item2 in list2:
                        if item2 in items_before_1 and list2.index(item2) > idx2:
                            warnings.warn(
                                "Detected conflicting order for '%s' and '%s' while merging media." % (item, item2),
                                MediaOrderConflictWarning,
                                stacklevel=2
                            )
                        elif item2 in items_after_1 and list2.index(item2) < idx2:
                            warnings.warn(
                                "Detected conflicting order for '%s' and '%s' while merging media." % (item2, item),
                                MediaOrderConflictWarning,
                                stacklevel=2
                            )
        
        # Merge the lists maintaining order
        return self._merge(*js)
    
    @property  
    def _css(self):
        """The _css property implementation."""
        css = self._css_lists
        return dict(
            (medium, self._merge(*[css_list for css_list in css if medium in css_list]))
            for medium in set(chain.from_iterable(css))
        )
    
    def _merge(self, *lists):
        """
        Merge multiple lists while trying to keep the relative order of elements.
        This is where the core merging logic happens.
        """
        # Algorithm to merge lists preserving order
        result = []
        lists = [list(l) for l in lists]  # Make copies
        
        while any(lists):
            # Find an element that can be added
            for lst in lists:
                if not lst:
                    continue
                    
                candidate = lst[0]
                # Check if this candidate appears at the head of its list in all lists that contain it
                can_add = True
                for other_list in lists:
                    if candidate in other_list and other_list.index(candidate) > 0:
                        # This candidate appears in another list but not at the head
                        can_add = False
                        break
                
                if can_add:
                    # Add the candidate to result and remove from all lists
                    result.append(candidate)
                    for l in lists:
                        if candidate in l:
                            l.remove(candidate)
                    break
            else:
                # No safe candidate found - we have a conflict
                # Just take from the first non-empty list
                for lst in lists:
                    if lst:
                        result.append(lst.pop(0))
                        break
        
        return result
    
    def __add__(self, other):
        """Combine two media objects."""
        return Media(
            js=self._js + (other._js if isinstance(other, Media) else other),
            css=self._merge_css(self._css, other._css if isinstance(other, Media) else other)
        )
    
    def _merge_css(self, css1, css2):
        """Merge two CSS dictionaries."""
        css = {}
        for medium in set(css1.keys()) | set(css2.keys()):
            css[medium] = []
            if medium in css1:
                css[medium].extend(css1[medium])
            if medium in css2:
                css[medium].extend(css2[medium])
        return css


def merge(*media_objects):
    """
    Merge multiple Media objects into one.
    This is the main merge function that would be called to combine media from multiple widgets.
    """
    if not media_objects:
        return Media()
    
    if len(media_objects) == 1:
        return media_objects[0]
    
    # Start with the first media object and add the rest
    result = Media()
    for media in media_objects:
        result = result + media
    
    return result


def _pairwise(iterable):
    """Return successive overlapping pairs taken from the input iterable."""
    a = iter(iterable)
    b = iter(iterable)
    next(b, None)
    return zip(a, b)


# Media types
MEDIA_TYPES = ('css', 'js')


# Example usage showing where MediaOrderConflictWarning would be raised:
if __name__ == "__main__":
    # Create media objects with conflicting order
    media1 = Media(js=['jquery.js', 'widget.js'])
    media2 = Media(js=['widget.js', 'jquery.js'])  # Different order
    
    # This would raise MediaOrderConflictWarning
    combined = merge(media1, media2)
    
    print("Combined JS files:", combined._js)