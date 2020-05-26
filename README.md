# Specifikace
Cílem projektu je implementace severu, který bude komunikovat protokolem HTTP a bude zajišťovat překlad doménových jmen. Pro překlad jmen bude server používat lokální resolver stanice na které běží - užijte přímo API, které poskytuje OS (například getnameinfo, getaddrinfo pro C/C++). 

## Server musí podporovat dvě operace:
### GET
Při použití této operace bude možné provést překlad jednoho dotazu, který bude specifikován jako parametr URL požadavku, například:
`GET /resolve?name=apple.com&type=A HTTP/1.1`
parametry jsou:
name = doménové jméno nebo IP adresa 
type = typ požadované odpovědi (A nebo PTR) 

Odpověď bude jeden řádek, který bude mít formát:
DOTAZ:TYP=ODPOVED
Tedy například:
`apple.com:A=17.142.160.59`

V případě nalezení odpovědi bude výsledek 200 OK. Není-li odpověď nalezena potom je odpověď 404 Not Found.
### POST
Metoda POST bude obsahovat v těle požadavku seznam dotazů, každý na samostatném řádku. Řádek požadavku je: 
`POST /dns-query HTTP/1.1`

Řádek v těle obsahující jeden dotaz bude mít následující formát:
DOTAZ:TYP
kde:
DOTAZ - představuje doménové jméno nebo IP adresu
TYP - je typ požadované odpovědi, tj., A nebo PTR

Například:
```
www.fit.vutbr.cz:A
apple.com:A
147.229.14.131:PTR
seznam.cz:A
```
Výsledkem bude 200 OK (krom případů uvedených níže) a seznam odpovědí. 
Odpověď musí obsahovat seznam nalezených odpovědí. V případě, že pro uvedený dotaz nebyla odpověď nalezena, pak tento nebude uveden v odpovědích. 

### Ošetření chyb
Mohou nastat následující chyby, které nesouvisí s výsledkem při překladu dotazů:
* Vstupní URL není správné, je jiné než /resolve či /dns-query - vrací 400 Bad Request.
* Vstupní parametry pro GET jsou nesprávné nebo chybí - vrací 400 Bad Request.
* Formát vstupu pro POST není správný - vrací 400 Bad Request.
* Operace není podporována - je použita jiná operace než GET a POST - vrací 405 Method Not Allowed.
* Pro ostatní nestandardní případy je návratová hodnota 500 Internal Server Error.

### Testování
Pro testování je možné použít nástroj curl. Příklady níže uvažují, že server obsluhuje lokální port 5353.

##### Příklad příkazu pro GET operaci:

`curl localhost:5353/resolve?name=www.fit.vutbr.cz\&type=A`

Odpověď/výstup z curl by měl být jeden řádek:
`www.fit.vutbr.cz:A=147.229.9.23`

##### Příklad příkazu pro POST operaci:

`curl --data-binary @queries.txt -X POST http://localhost:5353/dns-query`

Kde soubor queries.txt obsahuje toto:
```
www.fit.vutbr.cz:A
www.google.com:A
www.seznam.cz:A
147.229.14.131:PTR
ihned.cz:A
```

odpověď/výstup z curl by měla vypadat takto:
```
www.fit.vutbr.cz:A=147.229.9.23
www.google.com:A=216.58.201.68
www.seznam.cz:A=77.75.74.176
147.229.14.131:PTR=dhcpz131.fit.vutbr.cz
ihned.cz:A=46.255.231.42
```
