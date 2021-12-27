## Project setup update

0. Uninstall pyenv if it's old
1. Install pyenv (`curl https://pyenv.run | bash`)
2. Install python 3.10.1 (`pyenv install 3.10.1` and `pyenv global 3.10.1`)
3. Clone the repo and `cd` into it
4. Create a virtual env (`python -m venv env`)
5. Start a shell with the virtual env (`source env/bin/activate`)
6. Install dependencies (`python -m pip install -r requirements.txt`)
7. Test the exploits! (`python CRIME-cbc-poc.py`)

---

# CVE-2012-4929 alias CRIME

_Une attaque sur TLS/SSL_

Description officielle (traduite) :

> Les protocoles TLS 1.2 et antérieurs, tels qu'utilisés par Mozilla Firefox, Google Chrome, Qt, et d'autres produits, peuvent chiffrer des données compressées sans prendre le soin dissimuler la longueur des données en clair. Cela permet, par des attaques d'homme du milieu, d'obtenir les en-têtes HTTP en clair en observant les différences de longueur entre différentes requêtes dans lesquelles une chaîne de la requête est partiellement égale à la chaîne inconnue placée dans un en-tête HTTP. Cette attaque est aussi connue sous le nom de "CRIME".

## Principe

Le protocole TLS 1.2 propose d'utiliser un mécanisme de compression, DEFLATE, avant de chiffrer les données. Cet algorithme fonctionne en cherchant les motifs répétés, et en remplaçant les occurrences de ce motif par un jeton beaucoup plus court.

![Exemple de compression avec DEFLATE](./images/deflate.svg)

De la même façon, un attaquant peut observer si l'algorithme DEFLATE trouve un motif dans une requête HTTP qu'il ne maîtrise que partiellement, dans le but de deviner ce motif octet par octet, en observant uniquement la longueur du message compressé.

### Application

Pour réaliser cette attaque il faut remplir 2 conditions :

- Pouvoir exécuter du JavaScript sur la machine de la victime ; par exemple la victime ouvre un site malveillant en cliquant sur une publicité
- Pouvoir écouter les requêtes envoyées par la victime ; par exemple en faisant de l'empoisonnement de cache ARP

En JavaScript, un attaquant peut envoyer une requête à n'importe quel site, mais ne peut pas contrôler qu'un seul en-tête de la requête, l'adresse de destination, les autres en-têtes étant gérés par le navigateur.

Par exemple, un attaquant essaie de deviner la valeur du cookie `SESSIONID` en envoyant des requêtes sur une image du site `www.banque.fr`. Après compression, ces requêtes deviennent :

![Exemple d'envoi de requêtes à www.banque.fr](./images/sessionid.svg)

On constate que le message est plus court d'un octet dans le dernier cas, et par conséquent, l'attaquant peut déduire que le secret commence par un `c`.

Cependant, l'attaque n'est pas aussi simple car le message est chiffré après avoir été compressé. Il y a deux chiffrements vulnérables : RC4 et AES-CBC.

- Le cas de RC4 est trivial : le message chiffré fait la longueur du message compressé, l'attaque est directe et se fait comme décrite au dessus.
- Le cas de AES-CBC est plus complexe : le message chiffré a une taille qui est toujours un multiple de 16, il faut alors jouer avec le remplissage en bord de bloc.

## Preuve de Concept

Ici-même.

## Sources

- Martial Puygrenier : https://github.com/mpgn/CRIME-poc
- Thomas Pornin : https://security.stackexchange.com/questions/19911
