from helper_functions_peru import is_json

 
json_returned = '{dfsdf"name":"tim", "age":"64"}fff'

open_brace_index = json_returned.find("{")
json_returned = json_returned[open_brace_index:]
close_brace_index = json_returned.rfind("}")
json_returned = json_returned[:close_brace_index+1]


print(json_returned)
print(is_json(json_returned))


exit()

# r for raw - fixes the escaping of quotes
this_json = r'{"verbatim": "PERU\nFABACEAE\nAbarema adenophora (Ducke) Barneby & J.W. Grimes\ndet. D.A. Neill (MO), 2005\nAmazonas: Bagua.\nSoldado Oliva. Carretera entre\nBagua-Imaza.\n660 m\n\"Arbusto 3 m, inflorescencias\nblanco-cremosas.\"\n07 Febrero 1999\nC. Díaz, M. Huamán, F. Salvador,\nO. Portocarrero & M. Medina 10647\nMISSOURI BOTANICAL GARDEN HERBARIUM (MO)\nNº 2304555\nFIELD MUSEUM\nOF NATURAL HISTORY\nThe Field Museum\nThe Field Museum (F)\ncopyright reserved"}'
print(is_json(this_json))
# True - event though we have quotes in the text

print(is_json('{"text":"tim"}'))
# True

print(is_json("{'text':'tim'}"))
# False - you must use double quotes to surround keys and values in JSON


print(is_json('[{"text":"tim"}]'))
# True - my problems is this

tim = "[Schofield]"
if tim[0] == "[": tim = tim[1:]
if tim[-1] == "]": tim = tim[:-1]

print(tim)





