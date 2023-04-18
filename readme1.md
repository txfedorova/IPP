# Implementační dokumentace k 2. úloze do IPP 2022/2023
Jméno a příjmení: Fedorova Tatiana
Login: xfedor14

## UML diagram



+--------------+
|   Context    |
|--------------|
| GF           |
| TF           |
| TF_flag      |
| __instance   |
| cnt_instr    |
| cnt_line     |
| input        |
| label        |
| program      |
| src          |
| st_data      |
| st_frame     |
| st_jump      |
|--------------|
| __init__     |
| get_instance |
+--------------+
                                                                                                         
                                                                                                         
                                                                                                         
                                                                                                         
+-----------+                                           +-------------+       +-------------------------+
|  Argument |                                           |     XML     |       |       Interpreter       |
|-----------|                                           |-------------|       |-------------------------|
| argument  |  ---->  [ argparse.ArgumentParser ]       | source_file |       | functions               |
|-----------|                                           |-------------|       | index                   |
| __init__  |                                           | __init__    |       | instr_done              |
| parse     |                                           | get_arg     |       | instr_order             |
| parse_arg |                                           | get_instr   |       |-------------------------|
+-----------+                                           | get_label   |       | __init__                |
                                                        | parse       |       |  add                    |
                                                        +-------------+       |  add_sub_mul_idiv       |
                                                                              +-------------------------+
                                                                              |  and                    |
                                                                              |  and_or                 |
                                                                              |  break                  |
                                                                              |  call                   |
                                                                              |  concat                 |
                                                                              |  create_frame           |
                                                                              |  defvar                 |
                                                                              |  dprint                 |
                                                                              |  eq                     |
                                                                              |  exit                   |
                                                                              |  get_char               |
                                                                              |  gt                     |
                                                                              |  idiv                   |
                                                                              |  int2char               |
                                                                              |  jump                   |
                                                                              |  jump                   |
                                                                              |  jumpifeq               |
                                                                              |  jumpifneq              |
                                                                              |  lt                     |
                                                                              |  lt_gt_eq               |
                                                                              |  move                   |
                                                                              |  mul                    |
                                                                              |  not                    |
                                                                              |  or                     |
                                                                              |  pop_frame              |
                                                                              |  pops                   |
                                                                              |  push_frame             |
                                                                              |  pushs                  |
                                                                              |  read                   |
                                                                              |  return                 |
                                                                              |  set_char               |
                                                                              |  stri2int               |
                                                                              |  strlen                 |
                                                                              |  sub                    |
                                                                              |  type                   |
                                                                              |  write                  |
                                                                              |  write_and_dprint       |
                                                                              | get_arg_type_and_value  |
                                                                              | get_frame               |
                                                                              | get_var_type_and_value  |
                                                                              | if_bool                 |
                                                                              | if_int                  |
                                                                              | if_string               |
                                                                              | if_varible              |
                                                                              | interpret               |
                                                                              | jump                    |
                                                                              | process_instruction_for |
                                                                              +-------------------------+
                           
                           
                           
                           
+-------------------------+
| argparse.ArgumentParser |
|-------------------------|
|                         |
+-------------------------+


      
## Implementace

### Argumenty
Na zacatku skript interpret.py zpracovava vstupni argumenty pres knihovnu argparse. Argumenty pro vstup jsou nasledovne: --source s vstupnim souborem s XML reprezentaci zdrojoveho kodu a --input
souborem s vstupy (musi byt uveden alespon jeden).

### XML
Pro parsovani XML se pouziva xml.etree.ElementTree. Skript na zacatku kontroluje, zda je struktura korene spravna, potom pokracuje prochazenim vsech polozek a kontrolou struktury instrukci a jejich argumentu. Behem parsovani skript vytvari novou strukturu programu

### Instrukce 
Pred interpretaci instrukci skript radi instrukce podle poradi, prochazi vsechny instrukce a ziskava vsechny navesti instrukce s poradim, aby provedl skoky. Potom je vse pripraveno pro interpretaci instrukci, skript postupuje jednu instrukci za druhou. Vyuziva pomocne funkce:
get_frame - vrati ramec (GF/TF/LF)
get_var_type_and_value - nastavi typ a hodnotu promenne
get_arg_type_and_value - vrati typ argumentu a hodnotu
jump - zajistuje spravny skok (na spravny label)

### OOP
Principy OOP byly vuyzity, ale neefektivne. Pouzite klasy jsou: Context (obsahuje vetsinu promennych pro sdileny pristup), Argument (probiha parsing argumentu), XML (probiha parsing XML souboru), Interpreter (obsahuje zbyle metody). Vysledne klasy nejsou logicke rozdeleny.

### Poznamky
Internet zdroje (manualy, stackoverflow) jsou uvedeny v komentářích.
