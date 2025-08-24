import os
from django.core.files.uploadedfile import InMemoryUploadedFile
from ..models import MediaFile

class MediaRepository:
    def create_media_file(self, uploaded_file, user):
        # Get file information
        original_name = uploaded_file.name
        file_size = uploaded_file.size
        mime_type = uploaded_file.content_type
        
        # Create media file instance
        media_file = MediaFile(
            original_name=original_name,
            uploaded_by=user,
            file_size=file_size,
            mime_type=mime_type
        )
        
        # Save the file
        media_file.file.save(original_name, uploaded_file)
        media_file.save()
        
        return media_file
    
    def get_media_file_by_id(self, file_id):
        try:
            return MediaFile.objects.get(id=file_id)
        except MediaFile.DoesNotExist:
            return None
    
    def delete_media_file(self, file_id):
        media_file = self.get_media_file_by_id(file_id)
        if media_file:
            # Delete the file from storage
            media_file.file.delete()
            # Delete the database record
            media_file.delete()
            return True
        return False