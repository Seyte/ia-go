<!--
Ce que doit contenir le README d'après le sujet : une description des points forts de votre joueur (faites court, listez les techniques, décrivez l’heuristique codée, précisez les structures de données, évoquez comment vous avez décidé d’utiliser telle ou telle technique, mettez en avant ce dont vous êtes le plus fier...).
-->

Pour coder notre joueur, nous avons commencé par un algorithme MinMax avec une heuristique simple (qui retourne la différence de pions présents sur le plateau).

Après avoir testé à différentes profondeurs, nous avons mis en place une approche par *iterative deepening* :
- un coup par défaut est choisi aléatoirement en début d'algorithme
- on met en place un signal à retardement (le temps prévu pour un coup représente 1% du temps restant)
- tant que le signal n'est pas déclenché, on stocke le meilleur coup possible pour chaque profondeur
- le signal est détecté par un bloc try/except, et le joueur retourne le meilleur coup pour la dernière profondeur explorée

Ensuite, nous avons amélioré notre heuristique en tenant compte également du nombre de pions capturés et du nombre de cases "encerclées" (cases seules entourées par 4 pions de la même couleur).

Le défaut de cet algorithme est que notre joueur avait tendance à viser les bords en début de partie, ce qui ne nous a pas semblé souhaitable. Nous avons donc mis en place trois phases de jeu (stockés dans une enum) :
- une phase d'ouverture, durant laquelle les premiers coups sont codés en dur
- une phase de début de partie, durant laquelle les coups sont restreints au  carré de 5x5 cases au centre du plateau
- enfin, une phase durant laquelle nous exécutons notre algorithme MinMax

Afin d'obtenir un joueur plus rapide, nous avons remplacé notre algorithme MinMax par une approche AlphaBeta.

Finalement, nous avons remplacé notre heuristique par un réseau de neurones entraîné de manière similaire à celle du TP noté.

Nous avons souhaité entraîner notre réseau sur une base de données plus grande que celle fournie dans le TP, nous avons donc simulé nous-mêmes des parties entre deux joueurs `gnugoPlayer`. Les détails de ce programme sont dans le fichier `dataset_building/make_dataset.py`. Malheureusement, nous avons créé très peu de parties supplémentaires de cette manière par manque de performance.