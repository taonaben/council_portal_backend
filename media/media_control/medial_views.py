import os
import mimetypes
from django.conf import settings
from django.http import HttpResponse, Http404
from wsgiref.util import FileWrapper

def media_view(request, path):
    """
    Displays an image or file stored in the media folder.
    """
    # Get the file path relative to the media folder
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    
    # Check if the file exists
    if not os.path.isfile(file_path):
        raise Http404("File does not exist")
    
    # Get the file contents
    wrapper = FileWrapper(open(file_path, 'rb'))
    response = HttpResponse(wrapper, content_type=mimetypes.guess_type(file_path)[0])
    response['Content-Length'] = os.path.getsize(file_path)
    response['Content-Disposition'] = 'inline; filename="%s"' % os.path.basename(file_path)
    
    return response