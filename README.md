# TFE horaires FPMS
## Architecture du modèle
![segmentBloc](https://user-images.githubusercontent.com/44674472/124121968-cf5dec80-da75-11eb-9d35-8828015290c2.png)
## Liens utiles
<ul>
  <li><a href="https://fr.slideshare.net/PhilippeLaborie/introduction-to-cp-optimizer-for-scheduling">Introduction aux concepts de CP Optimizer</a></li>
  <li><a href="https://www.ibm.com/docs/en/icos/20.1.0">Documentation de CP Optimizer</a></li>
  <li><a href="http://ibmdecisionoptimization.github.io/docplex-doc/cp/index.html">Documentation de docplex, l'API Python de CP Optimizer</a></li>
</ul>

## Installation en local
Les instructions suivantes sont valables pour l'OS Windows. Certaines adaptations doivent être faites pour d'autres OS.

### Prérequis
<ul>
  <li><a href="https://youtu.be/dQw4w9WgXcQ">Python 3.8</a> (Python 3.9+ n'est pas supporté par docplex)
  <li><a href="https://www.ibm.com/products/ilog-cplex-optimization-studio">IBM ILOG CPLEX Optimization Studio</a> (nécessite une license académique)
  <li>IDE Python avec gestion d'environnement virtuels (ex : <a href="https://www.jetbrains.com/fr-fr/pycharm/">PyCharm</a>, nécessite une license académique) 
</ul>

### Configuration
Tout d'abord, assurez-vous que la version de Python que vous utilisez est bien 3.8 (ou en-dessous). Vérifiez la version courante via l'instruction ``python -V`` en ligne de commandes. Si ce n'est pas le cas, modifiez les variables d'environnement de telle sorte que le ``python.exe`` de Python 3.8- soit accessible et relancez la commande ``python -V``.

Ensuite, lancez la commande ``python setup.py install`` depuis le dossier qui contient le script ``setup.py``. Celui-ci est situé au chemin d'accès suivant : ``<OptiStudioDir>/python/``, avec ``<OptiStudioDir>`` le dossier où est installé IBM ILOG CPLEX Optimization Studio. La commande lancée a pour effet de pouvoir appeler CP Optimizer depuis Python dans la version définie précédemment.

Enfin, créez un nouveau projet Python dans votre IDE et configurez-le avec un environnement virtuel utilisant la même installation Python. Choisir une autre installation ou une autre version de Python ne permettra pas de bénéficier de la commande ``python setup.py install`` lancée précédemment. 

Tout est à présent en ordre pour exécuter les scripts ``runModelXXX.py`` dans le dossier ``model`` de ce repo. Veillez en amont à installer les packages listés dans `requirements.txt` avec `pip install <package>` dans l'environnement virtuel et à modifier la première ligne de `cpo_config.py` pour pointer vers l'exécutable `cpoptimizer.exe`. Cette dernière étape ne devrait pas être nécessaire si ce .exe est défini comme variable d'environnement Windows (configuré par défaut à l'installation de IBM ILOG CPLEX Optimization Studio)

## Utilisation
Les contraintes, fonctions objectifs et autres fonctions utilitaires sont séparées dans des modules Python. Les scripts à lancer sont nommés `runModelXXX.py`, sont situés dans le dossier `/model` et utilisent les modules Python mentionnés. Pour toute explication sur les choix qui ont menés à l'application de telle ou telle contrainte, veuillez vous référer au rapport de TFE qui vous a été remis.

Les données chargées par les différents modèles prennent la forme de tableaux Excel `datasetXXX.xlsx`, présents dans le dossier `/data`. Les noms de feuilles et de colonnes sont écrits en dur dans le code : tout changement doit être répercuté dans les codes (Ctrl + Maj + R). Lorsque plusieurs entités sont listées dans une même cellule, le séparateur est la virgule `,` sans espace entre ces entités.
