Simulation d'évolution de créatures autonomes
Présentation générale

Le projet est une simulation d'évolution artificielle développée en Python, reposant sur Pygame pour le rendu graphique et NumPy pour les calculs neuronaux. L'objectif est de faire émerger des comportements autonomes chez une population de créatures uniquement par sélection naturelle, sans apprentissage supervisé ni renforcement classique.

Chaque créature possède un réseau neuronal entièrement déterminé par son ADN. Les poids (et désormais les biais) du réseau sont directement codés dans cet ADN, qui évolue au fil des générations par mutation.

L'ensemble de la simulation est organisé de manière modulaire, avec une séparation claire entre le moteur physique, les capteurs, le système neuronal, l'évolution génétique, le rendu graphique et les outils de journalisation.

Architecture du projet

Le projet est organisé autour de plusieurs composants principaux.

World

Le monde de simulation est responsable de :

la gestion des créatures ;
la gestion de la nourriture ;
la mise à jour de la grille spatiale ;
les collisions entre créatures et nourriture ;
la suppression des entités mortes ;
la synchronisation globale de chaque frame.

Le monde constitue le cœur de la boucle de simulation.

Simulation

La classe Simulation orchestre l'évolution.

Elle gère notamment :

la création de la population initiale ;
la durée d'une génération ;
la sélection naturelle ;
la mutation génétique ;
le renouvellement complet de la population.

Une génération peut se terminer soit lorsque :

toutes les créatures sont mortes ;
le nombre maximal de frames est atteint.
Creature

Chaque créature possède :

une position ;
une orientation ;
une vitesse ;
une réserve d'énergie ;
un score ;
une distance parcourue ;
un ADN ;
un réseau neuronal.

À chaque frame, une créature :

observe son environnement ;
calcule les sorties de son réseau ;
transforme ces sorties en commandes motrices ;
se déplace ;
perd progressivement de l'énergie.

Les créatures évoluent dans un monde torique : lorsqu'elles dépassent une frontière, elles réapparaissent de l'autre côté.

Réseau neuronal

Le cerveau est un réseau de neurones entièrement connecté comportant :

une couche d'entrée ;
deux couches cachées ;
une couche de sortie.

Les paramètres du réseau sont entièrement issus de l'ADN :

poids ;
biais.

Aucun apprentissage n'est réalisé pendant la vie d'une créature. Toute amélioration provient exclusivement de l'évolution génétique.

ADN

L'ADN est représenté sous la forme d'un vecteur de nombres flottants.

Il contient désormais :

tous les poids du réseau ;
tous les biais.

L'ADN peut :

être généré aléatoirement ;
être copié ;
être muté ;
être croisé ;
être exporté/importé en Base64.

Cette dernière fonctionnalité permet notamment de redémarrer une simulation à partir d'un individu particulier.

Capteurs

Les créatures perçoivent leur environnement grâce à un système de rayons.

Chaque rayon fournit :

la proximité d'un objet détecté ;
son type.

Les objets actuellement détectables sont :

nourriture ;
autres créatures.

Les rayons sont répartis uniformément dans un champ de vision configurable.

Raycaster

Le raycaster s'appuie sur une grille spatiale afin de limiter le nombre de tests de collision.

Chaque rayon interroge uniquement les cellules traversées avant de rechercher une éventuelle intersection avec les objets présents.

Cette approche réduit fortement le coût des recherches par rapport à un balayage complet de toutes les entités.

Spatial Grid

La grille spatiale découpe le monde en cellules.

Elle est utilisée par :

le raycaster ;
les collisions avec la nourriture.

Elle permet d'obtenir des performances satisfaisantes malgré un grand nombre d'entités.

Nourriture

La nourriture est générée :

au début de chaque génération ;
progressivement pendant la simulation selon un taux configurable.

Chaque nourriture :

possède une position ;
une taille ;
une valeur énergétique.

Lorsqu'une créature entre en collision avec elle, son énergie augmente et son score est incrémenté.

Sélection naturelle

À la fin d'une génération :

les créatures sont classées selon leur score ;
un pourcentage des meilleures est conservé ;
chaque nouvel individu est obtenu par mutation de l'un des survivants.

En cas d'extinction totale, une nouvelle population entièrement aléatoire est créée.

Interface graphique

Le rendu est assuré par Pygame.

L'affichage comprend :

les créatures ;
leur direction ;
la nourriture ;
les statistiques de simulation.

Un mode spectateur a également été ajouté.

Mode spectateur

Le mode spectateur permet d'observer individuellement une créature.

Fonctionnalités :

activation/désactivation au clavier ;
caméra suivant automatiquement la créature sélectionnée ;
changement de cible avec les flèches directionnelles ;
affichage prévu des rayons de perception de la créature observée.

Ce mode constitue un outil précieux pour analyser les comportements individuels et le fonctionnement des capteurs.

Performances

Le projet comporte déjà plusieurs optimisations :

utilisation de NumPy pour les calculs neuronaux ;
grille spatiale pour les recherches de voisinage ;
découpage clair de la boucle de simulation ;
instrumentation détaillée des temps d'exécution.

Les mesures actuelles montrent que la majeure partie du temps de calcul est consacrée à la mise à jour des créatures, tandis que la reconstruction de la grille, la gestion de la nourriture et le nettoyage représentent une faible part du coût total.

État actuel des fonctionnalités

Le projet dispose aujourd'hui des éléments suivants :

simulation d'évolution fonctionnelle ;
population entièrement autonome ;
réseau neuronal évolutif ;
ADN exportable et réutilisable ;
système de perception par rayons ;
grille spatiale ;
nourriture dynamique avec réapparition progressive ;
caméra ;
mode spectateur ;
suivi des performances ;
journalisation des décès ;
sélection naturelle basée sur les performances individuelles.
Axes d'amélioration

Le projet offre plusieurs perspectives d'évolution, notamment :

amélioration de la précision du système de raycasting et des capteurs ;
enrichissement des comportements possibles des créatures ;
diversification des critères de sélection naturelle au-delà du seul score alimentaire ;
introduction de nouvelles caractéristiques évolutives (champ de vision, vitesse maximale, taille, portée des capteurs, etc.) ;
amélioration de la dynamique de l'écosystème (gestion plus riche des ressources, interactions entre créatures, obstacles, zones d'intérêt) ;
optimisation des performances pour permettre des populations plus importantes ;
enrichissement des outils de visualisation et d'analyse des comportements individuels et collectifs ;
ajout d'outils d'analyse statistique de l'évolution des générations ;
amélioration de l'ergonomie de l'interface utilisateur et des contrôles de la simulation.

Dans son état actuel, le projet constitue déjà une base solide pour l'étude de comportements émergents et de mécanismes d'évolution artificielle, tout en restant suffisamment modulaire pour accueillir de nombreuses extensions futures.