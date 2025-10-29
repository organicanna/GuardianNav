"""
Tests pour les utilitaires partagés de GuardianNav
"""
import pytest
from guardian.utils import haversine, format_message_efficiently


class TestHaversine:
    """Tests pour la fonction haversine"""
    
    def test_haversine_same_point(self):
        """Test distance entre un même point"""
        coord = (48.8566, 2.3522)  # Paris
        distance = haversine(coord, coord)
        assert distance == 0.0
    
    def test_haversine_known_distance(self):
        """Test avec une distance connue approximative"""
        # Paris -> Versailles (environ 17 km)
        paris = (48.8566, 2.3522)
        versailles = (48.8049, 2.1204)
        distance = haversine(paris, versailles)
        # La distance devrait être autour de 17 km (17000 m)
        assert 16000 < distance < 18000
    
    def test_haversine_short_distance(self):
        """Test pour une courte distance"""
        # Deux points très proches (environ 100m)
        coord1 = (48.8566, 2.3522)
        coord2 = (48.8576, 2.3522)
        distance = haversine(coord1, coord2)
        # Devrait être environ 100-150m
        assert 100 < distance < 150
    
    def test_haversine_caching(self):
        """Test que le cache fonctionne"""
        coord1 = (48.8566, 2.3522)
        coord2 = (48.8049, 2.1204)
        
        # Premier appel
        dist1 = haversine(coord1, coord2)
        
        # Second appel (devrait utiliser le cache)
        dist2 = haversine(coord1, coord2)
        
        # Les résultats doivent être identiques
        assert dist1 == dist2
    
    def test_haversine_symmetry(self):
        """Test que la distance est symétrique"""
        coord1 = (48.8566, 2.3522)
        coord2 = (48.8049, 2.1204)
        
        dist_forward = haversine(coord1, coord2)
        dist_backward = haversine(coord2, coord1)
        
        # La distance dans les deux sens doit être la même
        assert abs(dist_forward - dist_backward) < 0.01


class TestFormatMessage:
    """Tests pour le formatage de messages"""
    
    def test_format_message_basic(self):
        """Test formatage de base"""
        result = format_message_efficiently("Line 1", "Line 2", "Line 3")
        expected = "Line 1\nLine 2\nLine 3"
        assert result == expected
    
    def test_format_message_with_empty_strings(self):
        """Test avec des chaînes vides qui doivent être filtrées"""
        result = format_message_efficiently("Line 1", "", "Line 2", None, "Line 3")
        expected = "Line 1\nLine 2\nLine 3"
        assert result == expected
    
    def test_format_message_single_part(self):
        """Test avec une seule partie"""
        result = format_message_efficiently("Single line")
        assert result == "Single line"
    
    def test_format_message_empty(self):
        """Test avec toutes les parties vides"""
        result = format_message_efficiently("", None, "")
        assert result == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
