# sentiment-app

Classification binaire d'avis français avec TF-IDF et régression logistique.

Installer : `pip install sentiment_app-1.0.0-py3-none-any.whl`.

```python
from sentiment_app import predict
print(predict("Service impeccable et livraison en avance"))
```

CLI : `sentiment "Produit cassé à l'arrivée" --json` ; `sentiment --version`.

Le modèle embarqué est entraîné sur 290 exemples synthétiques. Il ne mesure
pas l'urgence et peut mal interpréter l'ironie et les avis mitigés. Le score
n'est pas une probabilité calibrée. Le paquet renvoie positive/negative ;
l'abstention à 0,60 appartient au contrat de l'API.
