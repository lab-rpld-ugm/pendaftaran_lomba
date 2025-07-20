import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app


class FileHandler:
    """Utility class for secure file upload handling"""
    
    # Allowed file extensions for different file types
    ALLOWED_EXTENSIONS = {
        'image': {'jpg', 'jpeg', 'png', 'gif'},
        'document': {'pdf', 'doc', 'docx'},
        'profile_photo': {'jpg', 'jpeg', 'png', 'pdf'},
        'twibbon': {'jpg', 'jpeg', 'png'},
        'academic_math': {'pdf', 'doc', 'docx'},
        'academic_science': {'pdf', 'doc', 'docx'},
        'academic_logic': {'pdf', 'doc', 'docx'},
        'academic_informatics': {'pdf', 'doc', 'docx', 'py', 'cpp', 'java', 'txt', 'zip', 'rar'},
        'submission': {'pdf', 'doc', 'docx', 'py', 'cpp', 'java', 'txt', 'zip', 'rar'}
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'image': 5 * 1024 * 1024,      # 5MB
        'document': 10 * 1024 * 1024,  # 10MB
        'profile_photo': 5 * 1024 * 1024,  # 5MB
        'twibbon': 3 * 1024 * 1024     # 3MB
    }
    
    @staticmethod
    def allowed_file(filename, file_type='image'):
        """Check if file has allowed extension for given type"""
        if not filename:
            return False
        
        allowed_extensions = FileHandler.ALLOWED_EXTENSIONS.get(file_type, set())
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def get_file_extension(filename):
        """Get file extension from filename"""
        if not filename or '.' not in filename:
            return ''
        return filename.rsplit('.', 1)[1].lower()
    
    @staticmethod
    def generate_unique_filename(original_filename, prefix=''):
        """Generate unique filename with timestamp and UUID"""
        if not original_filename:
            return None
        
        # Get file extension
        extension = FileHandler.get_file_extension(original_filename)
        
        # Generate unique identifier
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        # Create filename
        if prefix:
            filename = f"{prefix}_{timestamp}_{unique_id}.{extension}"
        else:
            filename = f"{timestamp}_{unique_id}.{extension}"
        
        return filename
    
    @staticmethod
    def save_uploaded_file(file, subfolder, prefix='', file_type='image'):
        """
        Save uploaded file to specified subfolder with security checks
        
        Args:
            file: FileStorage object from form
            subfolder: Subfolder name within uploads directory
            prefix: Optional prefix for filename
            file_type: Type of file for validation
        
        Returns:
            tuple: (success: bool, filename: str or error_message: str)
        """
        if not file or not file.filename:
            return False, 'Tidak ada file yang dipilih'
        
        # Check file extension
        if not FileHandler.allowed_file(file.filename, file_type):
            allowed_exts = ', '.join(FileHandler.ALLOWED_EXTENSIONS.get(file_type, []))
            return False, f'File harus berformat: {allowed_exts.upper()}'
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        max_size = FileHandler.MAX_FILE_SIZES.get(file_type, 5 * 1024 * 1024)
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            return False, f'Ukuran file maksimal {max_size_mb:.1f}MB'
        
        try:
            # Generate secure filename
            filename = FileHandler.generate_unique_filename(file.filename, prefix)
            
            # Create full path
            upload_folder = current_app.config['UPLOAD_FOLDER']
            subfolder_path = os.path.join(upload_folder, subfolder)
            
            # Ensure subfolder exists
            os.makedirs(subfolder_path, exist_ok=True)
            
            # Save file
            file_path = os.path.join(subfolder_path, filename)
            file.save(file_path)
            
            return True, filename
            
        except Exception as e:
            current_app.logger.error(f'Error saving file: {str(e)}')
            return False, 'Gagal menyimpan file. Silakan coba lagi.'
    
    @staticmethod
    def delete_file(filename, subfolder):
        """
        Delete file from specified subfolder
        
        Args:
            filename: Name of file to delete
            subfolder: Subfolder name within uploads directory
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not filename:
            return True  # Nothing to delete
        
        try:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, subfolder, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            
            return True  # File doesn't exist, consider it deleted
            
        except Exception as e:
            current_app.logger.error(f'Error deleting file {filename}: {str(e)}')
            return False
    
    @staticmethod
    def get_file_url(filename, subfolder):
        """
        Get URL for uploaded file
        
        Args:
            filename: Name of the file
            subfolder: Subfolder name within uploads directory
        
        Returns:
            str: URL path to the file
        """
        if not filename:
            return None
        
        return f'/uploads/{subfolder}/{filename}'
    
    @staticmethod
    def file_exists(filename, subfolder):
        """
        Check if file exists in specified subfolder
        
        Args:
            filename: Name of file to check
            subfolder: Subfolder name within uploads directory
        
        Returns:
            bool: True if file exists, False otherwise
        """
        if not filename:
            return False
        
        try:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, subfolder, filename)
            return os.path.exists(file_path)
        except:
            return False


def save_uploaded_file(file, folder='uploads', prefix=''):
    """
    Simple function to save uploaded file with security checks
    
    Args:
        file: FileStorage object from form
        folder: Folder name within uploads directory
        prefix: Optional prefix for filename
    
    Returns:
        str: Saved filename
    
    Raises:
        Exception: If file cannot be saved
    """
    if not file or not file.filename:
        raise Exception('Tidak ada file yang dipilih')
    
    # Generate secure filename
    filename = FileHandler.generate_unique_filename(file.filename, prefix)
    
    # Create full path
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/uploads')
    folder_path = os.path.join(upload_folder, folder)
    
    # Ensure folder exists
    os.makedirs(folder_path, exist_ok=True)
    
    # Save file
    file_path = os.path.join(folder_path, filename)
    file.save(file_path)
    
    return filename


def get_upload_path(folder='uploads'):
    """Get the upload path for a specific folder"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/uploads')
    return os.path.join(upload_folder, folder)


def validate_academic_file(file, competition_type):
    """
    Validate file for academic competitions with specific rules
    
    Args:
        file: FileStorage object from form
        competition_type: Type of competition (math, science, logic, informatics)
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not file or not file.filename:
        return False, 'File wajib diupload untuk kompetisi akademik'
    
    # Get file extension
    extension = FileHandler.get_file_extension(file.filename)
    
    # Check allowed extensions based on competition type
    allowed_extensions = FileHandler.ALLOWED_EXTENSIONS.get(f'academic_{competition_type.lower()}', set())
    
    if extension not in allowed_extensions:
        allowed_list = ', '.join(allowed_extensions).upper()
        return False, f'File untuk kompetisi {competition_type} harus berformat: {allowed_list}'
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    # Academic files can be up to 15MB (larger than regular documents)
    max_size = 15 * 1024 * 1024  # 15MB
    if file_size > max_size:
        return False, 'Ukuran file maksimal 15MB untuk kompetisi akademik'
    
    # Additional validation for programming files
    if competition_type.lower() == 'informatics' and extension in ['py', 'cpp', 'java']:
        # Basic validation for code files
        try:
            file.seek(0)
            content = file.read().decode('utf-8', errors='ignore')
            file.seek(0)
            
            # Check if file is not empty
            if len(content.strip()) < 10:
                return False, 'File kode tidak boleh kosong atau terlalu pendek'
            
            # Basic syntax check for common issues
            if extension == 'py' and 'import' not in content and 'def' not in content and 'print' not in content:
                return False, 'File Python tampaknya tidak valid (tidak ada import, def, atau print)'
            
        except UnicodeDecodeError:
            return False, 'File kode harus berupa text file yang valid'
        except Exception:
            # If we can't read the file, allow it but log the issue
            pass
    
    return True, None


def save_academic_submission(file, user_id, competition_id, competition_type):
    """
    Save academic competition submission with proper naming and organization
    
    Args:
        file: FileStorage object from form
        user_id: ID of the user submitting
        competition_id: ID of the competition
        competition_type: Type of competition (math, science, logic, informatics)
    
    Returns:
        str: Saved filename
    
    Raises:
        Exception: If file cannot be saved or is invalid
    """
    # Validate file first
    is_valid, error_message = validate_academic_file(file, competition_type)
    if not is_valid:
        raise Exception(error_message)
    
    # Generate descriptive prefix
    prefix = f'user_{user_id}_comp_{competition_id}_{competition_type.lower()}'
    
    # Save to academic submissions folder
    filename = save_uploaded_file(file, 'academic_submissions', prefix)
    
    return filename


def get_file_info(filename, subfolder='academic_submissions'):
    """
    Get information about an uploaded file
    
    Args:
        filename: Name of the file
        subfolder: Subfolder where file is stored
    
    Returns:
        dict: File information including size, extension, etc.
    """
    if not filename:
        return None
    
    try:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/uploads')
        file_path = os.path.join(upload_folder, subfolder, filename)
        
        if not os.path.exists(file_path):
            return None
        
        # Get file stats
        stat = os.stat(file_path)
        file_size = stat.st_size
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        # Get file extension and type
        extension = FileHandler.get_file_extension(filename)
        
        # Determine file type
        file_type = 'Unknown'
        if extension in ['pdf']:
            file_type = 'PDF Document'
        elif extension in ['doc', 'docx']:
            file_type = 'Word Document'
        elif extension in ['py']:
            file_type = 'Python Code'
        elif extension in ['cpp']:
            file_type = 'C++ Code'
        elif extension in ['java']:
            file_type = 'Java Code'
        elif extension in ['txt']:
            file_type = 'Text File'
        elif extension in ['zip', 'rar']:
            file_type = 'Archive File'
        
        return {
            'filename': filename,
            'size': file_size,
            'size_formatted': f"{file_size / 1024 / 1024:.2f} MB" if file_size > 1024*1024 else f"{file_size / 1024:.2f} KB",
            'extension': extension,
            'file_type': file_type,
            'modified_time': modified_time,
            'url': f'/uploads/{subfolder}/{filename}'
        }
        
    except Exception as e:
        current_app.logger.error(f'Error getting file info for {filename}: {str(e)}')
        return None


def create_file_preview_html(file_info):
    """
    Create HTML preview for uploaded file
    
    Args:
        file_info: File information dictionary from get_file_info()
    
    Returns:
        str: HTML string for file preview
    """
    if not file_info:
        return '<div class="alert alert-warning">File tidak ditemukan</div>'
    
    # Icon based on file type
    icon_map = {
        'pdf': 'fas fa-file-pdf text-danger',
        'doc': 'fas fa-file-word text-primary',
        'docx': 'fas fa-file-word text-primary',
        'py': 'fas fa-file-code text-success',
        'cpp': 'fas fa-file-code text-info',
        'java': 'fas fa-file-code text-warning',
        'txt': 'fas fa-file-alt text-secondary',
        'zip': 'fas fa-file-archive text-dark',
        'rar': 'fas fa-file-archive text-dark'
    }
    
    icon_class = icon_map.get(file_info['extension'], 'fas fa-file text-muted')
    
    html = f'''
    <div class="card">
        <div class="card-body">
            <div class="d-flex align-items-center">
                <div class="me-3">
                    <i class="{icon_class} fa-2x"></i>
                </div>
                <div class="flex-grow-1">
                    <h6 class="mb-1">{file_info['filename']}</h6>
                    <p class="mb-1 text-muted">{file_info['file_type']}</p>
                    <small class="text-muted">{file_info['size_formatted']}</small>
                </div>
                <div>
                    <a href="{file_info['url']}" class="btn btn-outline-primary btn-sm" target="_blank">
                        <i class="fas fa-download me-1"></i>Download
                    </a>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return html


def save_payment_proof(file, user_id, competition_id, payment_id):
    """
    Save payment proof file with proper naming and organization
    
    Args:
        file: FileStorage object from form
        user_id: ID of the user submitting
        competition_id: ID of the competition
        payment_id: ID of the payment
    
    Returns:
        str: Saved filename
    
    Raises:
        Exception: If file cannot be saved or is invalid
    """
    if not file or not file.filename:
        raise Exception('File bukti pembayaran harus diupload')
    
    # Check allowed extensions for payment proof
    allowed_extensions = {'jpg', 'jpeg', 'png', 'pdf'}
    extension = FileHandler.get_file_extension(file.filename)
    
    if extension not in allowed_extensions:
        allowed_list = ', '.join(allowed_extensions).upper()
        raise Exception(f'File bukti pembayaran harus berformat: {allowed_list}')
    
    # Check file size (max 10MB for payment proof)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        raise Exception('Ukuran file bukti pembayaran maksimal 10MB')
    
    # Generate descriptive prefix
    prefix = f'payment_proof_{user_id}_{competition_id}_{payment_id}'
    
    # Save to payment proofs folder
    filename = save_uploaded_file(file, 'payment_proofs', prefix)
    
    return filename