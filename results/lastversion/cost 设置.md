<!-- MarkdownTOC -->
# cost 设置
### Couts pour Gate Allocation / Reallocation ?
- Gate Alloc initial : Coût = \alpha^0 * contact/distance + Taxi time: Cik = 
  \alpha^0 = taxi_{max} * n_{max} = 1000 x 1000 = 1000000
  - Avion pouvant être à distance
    - 0 si au contact
    - 1 si pas au contact
  - Avion normalement au contact :
    - 0 si au contact
    - 10 si pas au contact

- Gate Realloc : Coût = \alpha^t (changement + contact/distance) + Taxi time Cik = 
  pour qu'une pénalité de changement/contact soit toujours plus importante
  qu'une diminution de taxi:
     \alpha^t = taxi_{max} * n_{max} = 1000 x 1000 = 1000000
  - Avion au contact
    - 0 si pas de changement
    - 1 si changement au contact proche (dans le même terminal)
    - 10 si changement au contact loin (dans un autre terminal)
    - 100 si changement à distance
  - Avion à distance initialement au contact
    - 0 si changement au contact
    - 1 si pas de changement
    - 10 si changement a une autre a distance
  - Avion à distance dès le début
    - 0 si pas de changement
    - 1 si changement au contact
    - 10 si changement a une autre a distance

notation pour la définition du coût (pas très au point):
 - c^0_{i,k} = f^0(distance, taxi)
 - c^t_{i,k} = f(changement(=g(x^{t-1}_{i,k})), distance(=h(x^0_{i,k})), taxi)

<!-- /MarkdownTOC -->
