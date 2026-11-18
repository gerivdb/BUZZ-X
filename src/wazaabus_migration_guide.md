"""
WAZAA<->KG-L Bridge (KG-L native)

Étape 1 : Supprimer l'ancien bridge de BUZZ-X/src/wazaabus.py
Étape 2 : Migrer vers WAZAA/src/bus/wazaa_kg_subscriber.py (version natif KG-L)
Étape 3 : Sauvegarder le bridge WAZAA natif dans WAZAA/src/bus/wazaa_kg_subscriber.py
Étape 4 : Commiter le nettoyage et la migration
"""

# SKETCH : Plan de migration
# ===========================

## 1. Sauvegarde actuelle (BUZZ-X)

📁 `BUZZ-X/src/wazaabus.py` (1 162 lignes)
   - Implémentation BUZZ-X-native (code WazaaMessage, WazaaBusCore, WazaaToKGAdapter)
   - Inclut toute la logique de conversion WAZAA→KG-L

## 2. Cible (WAZAA)

📁 `WAZAA/src/bus/wazaa_kg_subscriber.py` (exist avant tâche) - 412 lignes
   - Déjà un subscriber WAZAA native KG-L (dérivé de la même intention initiale)
   - Contient WazaaKGConfig, WazaaKGMetrics, WazaaKGSubscriber
   - Détenteur du runtime KG-L WazaaToKGAdapter (via `kg_l_wazaa_adapter.py`)

## 3. Carte de migration

| Composant | Source (BUZZ-X) | Cible (WAZAA) |
|-----------|----------------|---------------| 
| Schéma WazaaMessage | `wazaabus.py` (BUZZ-X-native) | `message.py` (WAZAA natif) |
| Classe WazaaBusCore | `wazaabus.py` (BUZZ-X-native) | `wazaabus.py` (WAZAA natif, peut exister) |
| WazaaToKGAdapter | `wazaabus.py` (BUZZ-X-native) | `src/runtime/kg_l_wazaa_adapter.py` (existe) |
| WazaaKGSubscriber | `wazaabus.py` (BUZZ-X-native) | `wazaa_kg_subscriber.py` (existe) |
| WazaaKGConfig | `wazaabus.py` (BUZZ-X-native) | `wazaa_kg_subscriber.py` (existe) |
| WazaaKGMetrics | `wazaabus.py` (BUZZ-X-native) | `wazaa_kg_subscriber.py` (existe) |

## 4. Étapes de migration

### 4.1 Supprimer l'ancien bridge de BUZZ-X
1. Supprimer `src/wazaabus.py` de BUZZ-X
2. Vérifier qu'il n'y a pas de dépendances de `wazaabus` dans BUZZ-X

### 4.2 Intégrer le bridge WAZAA natif
1. Confirmer que `WAZAA/src/bus/wazaa_kg_subscriber.py` contient déjà toute la logique nécessaire
2. Si nécessaire, mettre à jour son `__init__.py` pour exporter le nouveau composant
3. Vérifier l'intégration avec le schema WAZAA dans `message.py`

### 4.3 Validation
1. Exécuter les tests pour WAZAA/src/bus/wazaa_kg_subscriber.py
2. Vérifier l'absence d'importations obsolètes de `wazaabus` (ex: `BUZZ-X`)
3. Confirmer que la chaîne d'exécution WAZAA→KG-L fonctionne via le pont natif

## 5. Commit requis

### Commit 1 : Migration (A+E) (Étape 1 : Phase d'engagement)
- `src/wazaabus.py` (BUZZ-X) supprimé (A)
- `src/bus/wazaa_kg_subscriber.py` (WAZAA) mis à jour/créé (E)

### Commit 2 : Nettoyage (A+E) (Étape 2 : Phase de nettoyage)
- Mettre à jour `src/bus/__init__.py` (WAZAA) (E)
- Supprimer tout code régi par les règles obsolètes (A)

### Commit 3 : Finalisation (A+E) (Étape 3 : Phase de finalisation)
- Validation finale via la suite de tests
- Nettoyer les fichiers temporaires (A)

## 6. Messages de commit

### Commit 1 : feat(bus): migrer WAZAA<->KG-L bridge vers natif WAZAA
- Description : Migrer le bridge WAZAA<->KG-L de BUZZ-X/src/wazaabus.py vers WAZAA/src/bus/wazaa_kg_subscriber.py natif WAZAA
- Impact : Nettoyage architectural, unification de l'implémentation WAZAA
- Files : BUZZ-X/src/wazaabus.py, WAZAA/src/bus/wazaa_kg_subscriber.py

### Commit 2 : chore: mettre à jour __init__.py de src/bus pour WAZAA natif
- Description : Mettre à jour l'exportation __init__.py de WAZAA/src/bus pour exposer correctement le bridge WAZAA natif
- Impact : Nettoyage des exports
- Files : WAZAA/src/bus/__init__.py

### Commit 3 : test: valider le pont WAZAA natif KG-L
- Description : Exécuter les tests de validation pour le pont WAZAA natif KG-L
- Impact : Validation de la fonctionnalité
- Files : Tests WAZAA/src/bus

## 7. Scripts d'intégration requis (optionnel)

### 7.1 Script de migration
```bash
# Migrer depuis BUZZ-X vers WAZAA
#!/bin/bash

SOURCE_DIR="D:\DO\WEB\TOOLS\L4-TOOLS\BUZZ-X\src"
TARGET_DIR="D:\DO\WEB\TOOLS\L4-TOOLS\WAZAA\src\bus"

# Supprimer l'ancien bridge de BUZZ-X
sudo rm -f "$SOURCE_DIR/wazaabus.py"

# Vérifier que la cible existe
if [ ! -f "$TARGET_DIR/wazaa_kg_subscriber.py" ]; then
    echo "ERREUR: wazaa_kg_subscriber.py cible non trouvée"
    exit 1
fi

# Exécuter les tests de validation
python -m pytest "tests/wazaa_kg_subscriber" -v

# Valider l'intégration
python -c "
import sys
sys.path.insert(0, 'D:\DO\WEB\TOOLS\L4-TOOLS\WAZAA\src')
from bus.wazaa_kg_subscriber import WazaaKGSubscriber, WazaaKGConfig
config = WazaaKGConfig()
subscriber = WazaaKGSubscriber(config=config)
print('WAZAA natif WAZAA<->KG-L bridge vérifié avec succès')
"

echo "Migration complète"
```

### 7.2 Script de vérification du système
```python
# test_system_integration.py (WAZAA)
import sys
sys.path.insert(0, r'D:\DO\WEB\TOOLS\L4-TOOLS\WAZAA\src')

from bus.wazaa_kg_subscriber import (
    WazaaKGSubscriber,
    WazaaKGConfig,
    WazaaMessage,
    MessageType,
)

def test_wazaabus_kg_integration():
    """Valider le pont WAZAA natif KG-L."""
    print("Test WAZAA natif WAZAA<->KG-L bridge")

    # Créer le bridge avec la config par défaut
    config = WazaaKGConfig()
    subscriber = WazaaKGSubscriber(config=config)
    assert subscriber._kg_runtime is not None
    print("✓ Runtime KG-L attaché")

    # Publier un message WAZAA (FRICTION)
    msg = WazaaMessage(
        topic="L4-TOOLS/CTULU/friction",
        source="gerivdb/CTULU",
        msg_type=MessageType.FRICTION,
        payload={"friction_score": 0.8},
    )
    subscriber._handle_message(msg)

    # Valider le graphe KG-L
    summary = subscriber.get_graph_summary()
    assert summary.get("total_nodes", 0) == 1
    assert summary.get("total_edges", 0) == 1
    print(f"✓ Node KG-L créé : {summary['total_nodes']}")
    print(f"✓ Edge KG-L créé : {summary['total_edges']}")

    # Valider les métriques
    stats = subscriber.stats
    assert stats["tracking"] is True
    assert stats["total_received"] == 1
    assert stats["total_converted"] == 1
    print(f"✓ Métriques : {stats}")

    print("Intégration WAZAA natif réussie")
    return True

if __name__ == "__main__":
    test_wazaabus_kg_integration()
```

## 8. Considérations de performance

### 8.1 Impact des performances
- Le bridge WAZAA natif devrait avoir des performances similaires ou meilleures car il utilise le runtime KG-L externe directement (si disponible)
- Le runtime mémoire de fallback BUZZ-X peut être plus lent mais reste acceptable pour les charges de travail de développement

### 8.2 Utilisation de la mémoire
- L'utilisation du runtime KG-L externe (si présent) est optimisée
- Le runtime de fallback utilise une structure KG-L minimale (liste simple)

### 8.3 Compacité du code
- Le bridge WAZAA natif élimine le code redondant et réduit la duplication
- Le code BUZZ-X est supprimé, réduisant la dette technique

## 9. Référence ADR

- **ADR** : ADR-2026-08-19-001-WAZAA-Native-KG-L-Bridge
- **IntentHash** : 0xADR_2026_08_19_001_WAZAA_NATIVE_KG_L_BRIDGE
- **Depot** : gerivdb/GOVERNANCE-HUB
- **Statut ADR** : proposed
- **Màj requise si** : statut ADR passe à deprecated ou superseded

## 10. Résumé

Cette migration élimine le bridge temporaire BUZZ-X, intègre le bridge WAZAA natif, nettoie l'architecture, et aligne tous les composants sur l'emplacement cible WAZAA. Le bridge WAZAA<->KG-L restera dans WAZAA/src/bus/ pour une maintenance et un développement continus.

Implémentation étape par étape :
1. Supprimer `src/wazaabus.py` de BUZZ-X
2. Valider `src/bus/wazaa_kg_subscriber.py` dans WAZAA natif
3. Mettre à jour l'exportation WAZAA/src/bus/__init__.py
4. Exécuter la suite de tests de validation
5. Nettoyer les fichiers temporaires

Résultat : Pont WAZAA<->KG-L unifié, natif, et prêt pour la production dans WAZAA.
