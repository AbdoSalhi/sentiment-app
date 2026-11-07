# Semaine 5 : interface Streamlit

## 1. Pourquoi l'interface n'importe-t-elle jamais le modèle ?

La page `ui/app.py` ne connaît que `ui.client`. Le client envoie des requêtes
HTTP à `/health` et `/predict` ; il n'importe ni `api`, ni `src.predict`, ni
`joblib`. Le modèle reste chargé une seule fois dans le processus de l'API.
Cela conserve le même contrat de prédiction pour tous les clients : si le
modèle est réentraîné, la page n'a pas besoin d'être modifiée. Si l'API change
d'adresse, la variable d'environnement `API_URL` suffit à configurer le client.

Un test inspecte les imports des deux fichiers de l'interface pour vérifier
cette séparation. Les tests de la page remplacent uniquement la création
de la connexion par un `TestClient` : les avis passent bien par les routes
HTTP de la vraie API, sans appel direct au modèle depuis la page.

## 2. Que montre la page quand le modèle hésite ?

Pour « xqzvb wlkptr grombu », l'API répond `INDETERMINE`, score 0,5162.
La page affiche « Je ne sais pas : à faire vérifier par un humain », **52 %**,
et « La confiance est sous le seuil d'abstention : un humain doit trancher. »
Ce résultat a été vérifié avec AppTest et dans le navigateur contre l'API
locale. L'interface ne décide pas elle-même du seuil : elle affiche la
décision prise par le service du TP4.

Une abstention permet de transmettre un avis incertain à un humain au lieu
de présenter une polarité forcée comme un verdict fiable. Dans un fichier,
elle reste visible dans le tableau, le résumé et le CSV téléchargé ; le
score original est conservé.

## 3. Que voit l'utilisateur quand l'API tombe ?

La santé de l'API est vérifiée à chaque réexécution de la page. Une connexion
impossible affiche « API injoignable : lancez d'abord uvicorn api.main:app. »
Si le service ne répond pas dans le délai de dix secondes, un message
distinct invite à réessayer. Ces deux situations sont testées sans montrer
les détails internes des exceptions réseau.

Les autres erreurs sont traduites par le client :

| Situation | Message et affichage |
| --- | --- |
| Texte vide, blanc ou trop long, 422 | Avertissement « Texte refusé : vide, fait d'espaces, ou de plus de 2000 caractères. » |
| Modèle indisponible, 503 | Erreur « Modèle non chargé : le service est temporairement indisponible. » |
| Panne de prédiction, 500 | Erreur « Erreur interne de l'API (code 500). » |
| Réponse JSON mal formée ou incompatible | Erreur indiquant une réponse de l'API invalide |

Les essais de panne utilisent des transports HTTP simulés et AppTest ;
ils vérifient l'affichage après réexécution, sans arrêter le serveur utilisé
sur le poste. Un refus ou une panne dans un lot reste associé à sa ligne,
avec une confiance vide et une entrée `ERREUR` dans le résumé.

## 4. Fichier d'avis et téléchargement

`data/avis_exemple.csv` contient six avis. Le dépôt réel du fichier dans le
navigateur produit le tableau et le résumé suivants :

| Ligne | Verdict | Confiance |
| ---: | --- | ---: |
| 1 | Avis positif | 0,7770 |
| 2 | Avis négatif | 0,7465 |
| 3 | Je ne sais pas : à faire vérifier par un humain | 0,5162 |
| 4 | Avis positif | 0,7928 |
| 5 | Avis négatif | 0,7778 |
| 6 | Avis positif | 0,7647 |

Résumé : `{"INDETERMINE": 1, "NEGATIVE": 2, "POSITIVE": 3}`.
Un avis sur six est à faire vérifier par un humain.

Le bouton « Télécharger les résultats » produit `resultats.csv`, avec les
colonnes `text`, `verdict`, `confiance`. Le téléchargement a été effectué
dans le navigateur puis relu : six lignes, trois colonnes, accents préservés.
Le fichier est encodé en UTF-8 avec BOM pour faciliter son ouverture dans
Excel. Un test compare aussi les valeurs exportées au tableau affiché.

La page refuse proprement un fichier sans colonne `text`, vide, contenant
des guillemets non fermés ou un encodage incorrect. Un fichier ne contenant
que l'en-tête affiche un avertissement. Une cellule blanche est envoyée
comme texte blanc et refusée par l'API ; elle n'est pas transformée en
chaîne `nan` par pandas.

Comme dans le guide, chaque réexécution recalcule le lot, y compris au
téléchargement. Ce fonctionnement convient au fichier d'exemple ; un gros
volume demanderait une stratégie de cache ou un traitement par lots côté API.

## 5. Vérifications et lancement

Vérifications locales du 7 novembre 2026 :

- **43 nouveaux tests passent** : client HTTP, page AppTest, erreurs,
  import CSV et export.
- Suite complète : **132 passed, 2 xfailed**. Les deux échecs attendus sont
  les erreurs connues du jeu d'or du TP4, toujours déclarées en mode strict.
- Couverture de l'API : **100 %**, seuil de 95 % conservé.
- Ruff et mypy passent ; `pip check` ne signale aucun conflit.
- Le navigateur affiche l'API prête, « Avis positif » à 78 %, l'abstention
  à 52 % et le lot de six avis. AppTest vérifie aussi « Avis négatif » à 75 %.

Les versions de Streamlit et des dépendances du semestre sont conservées.
`virtualenv==20.35.*` est fixé dans les dépendances de développement pour
rester compatible avec `packaging<25`, requis par Streamlit 1.39.

Deux terminaux, dans la racine du dépôt, avec l'environnement activé :

```powershell
python -m uvicorn api.main:app --reload
```

```powershell
python -m streamlit run ui/app.py --server.headless true --browser.gatherUsageStats false
```

La page est disponible sur `http://127.0.0.1:8501`. La CI installe Streamlit,
entraîne le modèle et rejoue toute la suite avec Ruff, mypy et la couverture.
Le contrôle T34 se vérifie dans GitHub Actions après le push.
