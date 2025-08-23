import pytesseract
from PIL import Image
import re
import cv2
import numpy as np
from datetime import datetime
import pytesseract.pytesseract

def preprocess_image(image):
    """Preprocess image for better OCR results"""
    # Convert PIL to OpenCV format
    if hasattr(image, 'convert'):
        image = np.array(image)
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to get binary image
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Noise removal
    kernel = np.ones((1, 1), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    return binary

def extract_table_data(image):
    """Extract table-like data from image"""
    # Preprocess image
    processed_img = preprocess_image(image)
    
    # OCR configuration for better table recognition
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/\-.,:() '
    
    # Extract text
    text = pytesseract.image_to_string(processed_img, config=custom_config)
    
    return text

def parse_date_formats(date_str):
    """Parse various date formats commonly found in datasheets"""
    date_patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{1,2})\.(\d{1,2})\.(\d{2,4})',      # DD.MM.YYYY
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',   # YYYY/MM/DD or YYYY-MM-DD
        r'(\d{1,2})\s+(\w{3})\s+(\d{4})',        # DD MMM YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                if len(match.groups()) == 3:
                    if len(match.group(3)) == 2:  # YY format
                        year = '20' + match.group(3) if int(match.group(3)) < 50 else '19' + match.group(3)
                    else:
                        year = match.group(3)
                    
                    if pattern == r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})':  # YYYY-MM-DD
                        return f"{year}-{match.group(2).zfill(2)}-{match.group(1).zfill(2)}"
                    elif pattern == r'(\d{1,2})\s+(\w{3})\s+(\d{4})':  # DD MMM YYYY
                        month_names = {
                            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                        }
                        month = month_names.get(match.group(2).lower()[:3], '01')
                        return f"{year}-{month}-{match.group(1).zfill(2)}"
                    else:  # DD/MM/YYYY or DD-MM-YYYY
                        return f"{year}-{match.group(2).zfill(2)}-{match.group(1).zfill(2)}"
            except:
                continue
    
    return None

def extract_tasks_from_image(file):
    """Extract tasks from image with enhanced table recognition"""
    try:
        img = Image.open(file)
        
        # Extract text from image
        text = extract_table_data(img)
        
        # Split into lines and clean
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Find dates in the text
        date_pattern = r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})|(\d{1,2}\s+\w{3}\s+\d{4})|(\d{4}[/\-]\d{1,2}[/\-]\d{1,2})'
        
        tasks = []
        processed_lines = set()
        
        for line in lines:
            # Skip if line is too short or already processed
            if len(line) < 5 or line in processed_lines:
                continue
                
            # Find dates in this line
            dates = re.findall(date_pattern, line)
            
            if dates:
                for date_tuple in dates:
                    # Get the non-empty date from tuple
                    date_str = next((d for d in date_tuple if d), '')
                    if date_str:
                        parsed_date = parse_date_formats(date_str)
                        if parsed_date:
                            # Extract task title (remove date and clean)
                            title = re.sub(date_pattern, '', line).strip()
                            title = re.sub(r'[^\w\s\-\.]', ' ', title)  # Clean special chars
                            title = ' '.join(title.split())  # Remove extra spaces
                            
                            if title and len(title) > 2:
                                tasks.append({
                                    "title": title,
                                    "date": parsed_date,
                                    "original_text": line,
                                    "extracted_at": datetime.now().isoformat()
                                })
                                processed_lines.add(line)
                                break
        
        # If no tasks found with dates, try to extract any meaningful lines
        if not tasks:
            for line in lines:
                if len(line) > 10 and not re.search(r'^\d+$', line):  # Skip pure numbers
                    tasks.append({
                        "title": line[:100],  # Limit length
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "original_text": line,
                        "extracted_at": datetime.now().isoformat()
                    })
        
        return tasks
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return [{
            "title": "Error processing image",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "original_text": str(e),
            "extracted_at": datetime.now().isoformat()
        }]
