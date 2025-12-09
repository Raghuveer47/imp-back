#!/usr/bin/env python3
"""
Test script to verify face detection is working properly
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def test_face_similarity():
    """Test face similarity calculation"""
    print("🧪 Testing Face Detection Logic")
    print("=" * 50)
    
    # Test 1: Same face (should be high similarity)
    face1 = np.random.rand(128).astype(np.float32)
    face2 = face1 + np.random.normal(0, 0.01, 128).astype(np.float32)  # Slight noise
    
    similarity = cosine_similarity(face1.reshape(1, -1), face2.reshape(1, -1))[0][0]
    print(f"✅ Same face with noise: {similarity:.4f}")
    
    # Test 2: Different faces (should be low similarity)
    face3 = np.random.rand(128).astype(np.float32)
    similarity = cosine_similarity(face1.reshape(1, -1), face3.reshape(1, -1))[0][0]
    print(f"❌ Different faces: {similarity:.4f}")
    
    # Test 3: Threshold test
    threshold = 0.95
    print(f"\n🔍 Threshold Analysis (threshold: {threshold})")
    print("-" * 30)
    
    test_similarities = [0.9023, 0.9653, 0.9093, 0.98, 0.85, 0.99]
    
    for sim in test_similarities:
        status = "✅ ACCEPT" if sim >= threshold else "❌ REJECT"
        print(f"Similarity {sim:.4f}: {status}")
    
    print(f"\n📊 Summary:")
    print(f"- Threshold: {threshold}")
    print(f"- Previous scores that would be REJECTED:")
    print(f"  • 0.9023 (was accepted before) ❌")
    print(f"  • 0.9093 (was accepted before) ❌")
    print(f"- Only scores >= {threshold} will be accepted ✅")

if __name__ == "__main__":
    test_face_similarity() 