Ez egy Python web alkalmazás, amit Flask-al oldottam meg.

A célja, hogy egy lokális weboldalt hoz létre, amin lehet keresni változó csillagokat.
A keresőbe beírt változó csillagnevét utána a program ellenőrzi az AAVSO adatbázisában az api-ján keresztül.
És a programba beállított térkép méreteket és tájolásokat letölti a változó csillagról.
Ezt egy saját api-val csinálja így van vissza jelzés, hogy az adott térkép letöltése folyamatban van vagy már sikerült, vagy nem sikerült.
A térképeket kép formátumban tölti le egy mappába és egy JSON adatbázis fájlba írja, hogy miket töltött le.
Aztán a fő oldalon ki listázza, hogy melyik változó csillagokról van már letöltve kereső térkép. Ha megnyitjuk akkor azt listázza ki, hogy milyen tájolások mellet van letöltve milyen látómezővel.
Ha megnyitjuk az egyiket akkor az adott tájoláson belül lépegethetünk a nagyobb, illetve a kisebb látómezők között.
Az adott változó csillag oldalán egy program letölti az MCSE VCSSZ oldaláról az adott változó csillag észlelt fénygörbéjét az elmúlt egy évből.

A program még nincs teljesen kész, illetve később szeretném átültetni Android alkalmazásra.
