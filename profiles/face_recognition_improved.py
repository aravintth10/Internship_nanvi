import os
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import logging
from insightface.app import FaceAnalysis
import faiss
import cv2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# CONFIGURATION
# -------------------------------
EMBEDDING_DIM = 512
DEVICE_ID = -1  # -1 = CPU, >=0 = GPU
SIMILARITY_THRESHOLD = 0.6  # Minimum similarity score to consider a match

# -------------------------------
# GLOBAL FACE ANALYSIS + FAISS
# -------------------------------
face_app = None
faiss_index = None
id_map = []

def initialize_face_recognition():
    """Initialize the face recognition system"""
    global face_app, faiss_index
    
    try:
        # Initialize InsightFace
        face_app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        face_app.prepare(ctx_id=DEVICE_ID)
        
        # Initialize FAISS index
        faiss_index = faiss.IndexFlatIP(EMBEDDING_DIM)  # Cosine similarity
        
        logger.info("✅ Face recognition system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize face recognition: {e}")
        return False

# -------------------------------
# UTILITY FUNCTIONS
# -------------------------------
def load_image_from_url(image_url):
    """Load image from URL"""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        return np.array(img)
    except Exception as e:
        logger.error(f"Failed to load image from URL {image_url}: {e}")
        return None

def load_image_from_path(image_path):
    """Load image from local path"""
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        img = Image.open(image_path).convert("RGB")
        return np.array(img)
    except Exception as e:
        logger.error(f"Failed to load image from path {image_path}: {e}")
        return None

def extract_embedding(image_np):
    """Extract face embedding from image"""
    try:
        faces = face_app.get(image_np)
        if not faces:
            return None
        return faces[0]["embedding"]
    except Exception as e:
        logger.error(f"Failed to extract embedding: {e}")
        return None

def normalize_embedding(embedding):
    """Normalize embedding for cosine similarity"""
    return embedding / np.linalg.norm(embedding)

# -------------------------------
# FACE REGISTRATION AND MATCHING
# -------------------------------
def register_face_from_url(image_url, face_id):
    """Register a face from URL"""
    try:
        img_np = load_image_from_url(image_url)
        if img_np is None:
            return False
            
        embedding = extract_embedding(img_np)
        if embedding is None:
            logger.warning(f"No face detected in {image_url}")
            return False
            
        # Normalize embedding
        embedding = normalize_embedding(embedding)
        
        # Add to FAISS index
        faiss_index.add(np.array([embedding]))
        id_map.append(face_id)
        
        logger.info(f"✅ Registered '{face_id}' from {image_url}")
        return True
    except Exception as e:
        logger.error(f"❌ Registration failed for '{face_id}': {e}")
        return False

def register_face_from_path(image_path, face_id):
    """Register a face from local path"""
    try:
        img_np = load_image_from_path(image_path)
        if img_np is None:
            return False
            
        embedding = extract_embedding(img_np)
        if embedding is None:
            logger.warning(f"No face detected in {image_path}")
            return False
            
        # Normalize embedding
        embedding = normalize_embedding(embedding)
        
        # Add to FAISS index
        faiss_index.add(np.array([embedding]))
        id_map.append(face_id)
        
        logger.info(f"✅ Registered '{face_id}' from {image_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Registration failed for '{face_id}': {e}")
        return False

def match_face_from_url(image_url, top_k=5):
    """Match a face from URL against registered faces"""
    try:
        img_np = load_image_from_url(image_url)
        if img_np is None:
            return []
            
        embedding = extract_embedding(img_np)
        if embedding is None:
            logger.warning(f"No face detected in {image_url}")
            return []
            
        # Normalize embedding
        embedding = normalize_embedding(embedding)
        
        # Search in FAISS index
        query_embedding = np.array([embedding])
        scores, indices = faiss_index.search(query_embedding, k=min(top_k, len(id_map)))
        
        matches = []
        for i, (idx, score) in enumerate(zip(indices[0], scores[0])):
            if idx < len(id_map) and score >= SIMILARITY_THRESHOLD:
                confidence = score * 100  # Convert to percentage
                matches.append({
                    'id': id_map[idx],
                    'confidence': confidence,
                    'score': score
                })
        
        logger.info(f"🔍 Found {len(matches)} matches for {image_url}")
        return matches
        
    except Exception as e:
        logger.error(f"❌ Matching failed for {image_url}: {e}")
        return []

def match_face_from_path(image_path, top_k=5):
    """Match a face from local path against registered faces"""
    try:
        img_np = load_image_from_path(image_path)
        if img_np is None:
            return []
            
        embedding = extract_embedding(img_np)
        if embedding is None:
            logger.warning(f"No face detected in {image_path}")
            return []
            
        # Normalize embedding
        embedding = normalize_embedding(embedding)
        
        # Search in FAISS index
        query_embedding = np.array([embedding])
        scores, indices = faiss_index.search(query_embedding, k=min(top_k, len(id_map)))
        
        matches = []
        for i, (idx, score) in enumerate(zip(indices[0], scores[0])):
            if idx < len(id_map) and score >= SIMILARITY_THRESHOLD:
                confidence = score * 100  # Convert to percentage
                matches.append({
                    'id': id_map[idx],
                    'confidence': confidence,
                    'score': score
                })
        
        logger.info(f"🔍 Found {len(matches)} matches for {image_path}")
        return matches
        
    except Exception as e:
        logger.error(f"❌ Matching failed for {image_path}: {e}")
        return []

def get_best_match_score(image_url):
    """Get the best match score for an image URL"""
    matches = match_face_from_url(image_url, top_k=1)
    if matches:
        return matches[0]['score']
    return 0.0

def clear_registered_faces():
    """Clear all registered faces"""
    global faiss_index, id_map
    faiss_index = faiss.IndexFlatIP(EMBEDDING_DIM)
    id_map = []
    logger.info("🧹 Cleared all registered faces")

def get_registered_faces_count():
    """Get the number of registered faces"""
    return len(id_map)

# -------------------------------
# INITIALIZATION CHECK
# -------------------------------
def is_initialized():
    """Check if face recognition is initialized"""
    return face_app is not None and faiss_index is not None

# Initialize the system when module is imported
if not is_initialized():
    initialize_face_recognition() 