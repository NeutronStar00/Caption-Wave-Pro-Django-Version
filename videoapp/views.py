from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import os
from .video_processor import process_video_file

@csrf_exempt
def process_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        video_path = default_storage.save(video_file.name, video_file)
        
        try:
            output_path = process_video_file(video_path)
            
            if output_path and os.path.exists(output_path):
                response = FileResponse(open(output_path, 'rb'), content_type='video/mp4')
                response['Content-Disposition'] = 'attachment; filename="output_video.mp4"'
                return response
            else:
                return JsonResponse({'error': 'Video processing failed or output file not found'}, status=500)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
    return JsonResponse({'error': 'Invalid request'}, status=400)