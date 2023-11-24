# Magrana

Una pàgina web estàtica per cercar anagrames en català.

Prova-la a [anagrames.factoria.lu](https://anagrames.factoria.lu).

Un projecte de [Factoria Lunar](https://factoria.lu), fet per [Oriol Arcas](https://github.com/oriolarcas) i [Álvaro Martínez](https://github.com/alvaromartinezmajado).

## Com funciona

Hem confeccionat una base de dades amb les paraules en català (veure la següent secció), i les hem agrupat per paraules que són anagrames. Per exemple, "àguila" i "iguala" són anagrames i pertanyen al mateix grup.

Per agrupar les paraules es fa servir una clau comuna a totes elles, que consisteix en ordenar les seves lletres per ordre alfabètic, excloent accents o signes (guions, apòstrofs, punts volats, etc.). En el cas d'àguila i iguala, la clau és `aagilu`. Altres paraules amb la mateixa clau són igualà o aigual. La transformació de caràcters catalans a lletres de clau sense accents o símbols es desa en el fitxer [`index.js`](index.js).

La llista sencera de paraules és massa gran per incloure-la en la pàgina web directament, així que hem implementat un script, [`process.py`](process.py), que:

1. Llegeix la llista sencera de paraules.
2. Les agrupa per clau d'anagrama.
3. Inicialment, crea llistes d'anagrames segons la primera lletra de la clau d'anagrama (a, b, c...). Aquestes llistes són massa desiguals, per exemple les llistes a o e tenen molts anagrames, mentre que les u o x en tenen molt pocs.
4. Fragmenta cada llista usant un prefix més llarg (`aa`, `ab`, `ac`...). Si algun dels nous prefixos és massa gran, es torna a repetir (`aba`, `abb`, `abc`...).
5. Agrupa aquestes llites d'anagrames amb prefixos més llargs (`aaaee`) o menys (`u`), fins a formar blocs d'uns 512 KB. El resultat final es desa al directori [`data`](data) en format JSON. Per exemple, el fitxer `aacdd-aacdh.json` conté tots els anagrames la clau dels quals comença pels prefixos `aacdd`, `aacde`, `aacdf`, `aacdg`, `aacdh`.
6. L'índex de quins prefixos hi ha a cada fitxer JSON es desa en el fitxer [`index.js`](index.js).

Un cop tenim la base de dades de fitxers JSON i el fitxer [`index.js`](index.js), la pàgina web converteix la cerca de l'usuari en una clau d'anagrama (usant la transformació de caràcters) i consulta l'índex de fitxers JSON per trobar el prefix adient. Un cop troba el fitxer que conté el prefix de la clau d'anagrama, es decarrega aquell fitxer i consulta si existeix un anagrama amb aquella clau, i quines paraules conté.

## D'on venen les paraules

Les paraules provenen del corrector ortogràfic de [SoftCatalà](https://github.com/Softcatala/catalan-dict-tools).

## Llicència

D'aquest repositori: GPLv3.

De la [llista de paraules](https://github.com/Softcatala/catalan-dict-tools).
