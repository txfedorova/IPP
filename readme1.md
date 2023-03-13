# Implementační dokumentace k 1. úloze do IPP 2022/2023
Jméno a příjmení: Fedorova Tatiana
Login: xfedor14

## Implementace
Skript ```parse.php``` čte ze stdin argumenty pomocí funkce ```arg_read($argc, $argv)```. Tato funkce vrací buď nápovědu  (spuštění skriptu s argumentem ``` --help ```), nebo skončí s návratovým kódem 10 na stderr. Dále pomocí funkce ```input_read($output)```, která přijímá jako argument proměnnou outout (datový typ string), program v cyklu zpracovává vstup. Pomocí funkcí ```preg_replace```, ```trim``` se odstraní komentáře, nové řádky apod. Nastaví se hlavička na ```<program language="IPPcode23``` a příslušný flag ```header_flag = true```. Dále se uvnitř konstrukce ``` switch(strtoupper($string[0]))```se zpracová každý řádek instrukcí. Nejdřív se kontroluje počet argumentů pro každou instrukci ```if(sizeof($string) != 2)```, následně pomocí funkce ```preg_match``` se zjistí typ argumentů (var, nil, bool,int atd.). V případě, že se jedná o symbol, zpracování pokračuje do funkce ```symbol_read($symbol)```, kde se zjistí o který symbol (datový typ) jednalo, také provede se kontrola na escape sekvence. Na konci programu (pokud nebyla nalezená chyba) se vypíše řetězec ```output```.  Internet zdroje (manualy, stackoverflow) jsou uvedeny v komentářích.
Výsledný skript není přehledný kvůli nedostatečné dekompozici (nedostatečný počet funkcí).
