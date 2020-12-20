import math
from decimal import Decimal
from .models import Ingredient, MealType, Meal


def set_suitable_for_vegan():
    qs = Ingredient.objects.all()
    not_vegan = r'wurst|Wurst|wuerstchen|Wuerstchen|haehnchen|Haehnchen|speck|Speck|huhn|Huhn|con carne|leber|Leber|' \
                r'schinken|Schinken|fleisch|Fleisch|schwein|Schwein|lyoner|Lyoner|salami|Salami|ochsenschwanz|' \
                r'Ochsenschwanz|poekel|Poekel|Wiener-|(g|G)ulasch|cremesuppe|Cremesuppe|krebs|Krebs|' \
                r'gefluegel|Gefluegel|rind|Rind|kalb|Kalb|wildbruehe|Wildbruehe|wildsuppe|Wildsuppe|' \
                r'kaese|Kaese|mozzarella|Mozzarella|gouda|Gouda|brie|Brie|camembert|Camembert|' \
                r'emmentaler|Emmentaler|chester|Chester|edamer|Edamer|sahne|Sahne|butter|Butter|milchschoko|' \
                r'Milchschoko|milch|Milch|(c|C)arbonara|(p|P)resssack|(p|P)resskopf|' \
                r'mayo|Mayo|remoulade|Remoulade|tierisch|ueberwiegend pflanzlich|Salatcreme|' \
                r'fisch|Fisch|lachs|Lachs|sardellen|Sardellen|muschel|Muschel|hering|Hering|' \
                r'honig|Honig|spiegelei|Spiegelei|mit Ei |mit Ei,|Eier|Ei-|omlett|Omlett|Eischnee|(b|B)aiser|' \
                r'Schneekloess|Gelatine|Toast Hawaii|(k|K)asseler|(k|K)rabben|Welsh rarebit|(h|H)ummer|' \
                r'(w|W)ildkloesschen|(a|A)al|Gaisburger Marsch|Bauernfruehstueck|Jaegerfruehstueck|' \
                r'(h|H)uehner|Tiroler Geroestel|Berner Roesti|Labskaus|(h|H)uehnchen|Kaesetoast Allgaeuer Art|' \
                r'Wildsosse|Wildkraftbruehe|Koeniginsuppe|Bouillabaisse|eiweissarm|(l|L)atte'
    #qs.update(suitable_for=None)
    # set to vegan instantly
    '''qs = qs.exclude(lactose__gt=0).filter(key__regex=r'K[0-9]|Q[0-5]')
    qs.update(suitable_for='v')
    print(qs)
    print('\n')
    # set to vegan instantly second step
    qs = qs.exclude(lactose__gt=0).exclude(suitable_for='v').filter(key__regex=r'(B|C|D|F|G|H|N|P|R)[0-9]')\
        .exclude(name__regex=not_vegan)
    
    qs.update(suitable_for='v')
    # set to vegan instantly correction step
    qs = qs.exclude(lactose__gt=0).filter(name__regex=r'(k|K)okosmilch|(f|F)ruchtfleisch')
    qs.update(suitable_for='v')
    '''
    # more complex filtering
    qs_vegan = qs.exclude(suitable_for='v')
    qs_vegan = qs_vegan.exclude(lactose__gt=0)
    print(qs_vegan)
    print('\n')
    # exclude dairy, meats,
    qs_vegan = qs_vegan.exclude(key__regex=r'Q[6-9]|(E|M|T|U|V|W|Y)[0-9]')
    
    qs_vegan = qs_vegan.exclude(name__regex=not_vegan)
    print(qs_vegan)
    print(qs_vegan.count())
    with open('Output.txt', 'w',encoding="utf-8") as f:
        for item in qs_vegan.values_list('name',flat=True):
            print(item+'\n', file=f)
    qs_vegan.update(suitable_for='v')


def set_suitable_for_vegetarian():
    # vegan foods are also for vegeterians
    qs = Ingredient.objects.all().exclude(suitable_for='v')
    not_veggie = r'wurst|Wurst|wuerstchen|Wuerstchen|haehnchen|Haehnchen|speck|Speck|huhn|Huhn|con carne|leber|Leber|' \
                 r'schinken|Schinken|fleisch|Fleisch|schwein|Schwein|lyoner|Lyoner|salami|Salami|ochsenschwanz|' \
                 r'Ochsenschwanz|poekel|Poekel|Wiener-|Gulasch|krebs|Krebs|(a|A)al|Gaisburger Marsch|Bauernfruehstueck|' \
                 r'gefluegel|Gefluegel|rind|Rind|kalb|Kalb|wildbruehe|Wildbruehe|wildsuppe|Wildsuppe|Jaegerfruehstueck|' \
                 r'fisch|Fisch|lachs|Lachs|sardellen|Sardellen|muschel|Muschel|hering|Hering|(k|K)rabben|(h|H)ummer|' \
                 r'Toast Hawaii|(k|K)asseler|(p|P)resssack|(p|P)resskopf|(c|C)arbonara|(w|W)ildkloesschen|(h|H)uehner|' \
                 r'Tiroler Geroestel|Berner Roesti|Labskaus|(h|H)uehnchen|(k|K)rabben|Welsh rarebit|Kaesetoast Allgaeuer Art|' \
                 r'Wildsosse|Wildkraftbruehe|Koeniginsuppe|Bouillabaisse'
    # set to veggie instantly
    #qs = qs.filter(name__regex=r'(v|V)egetarisch')
    #qs.update(suitable_for='veggie')
    #qs = qs.filter(key__regex=r'E1')
    #qs.update(suitable_for='veggie')
    #print(qs)
    #print('\n')
    '''
    # set to vegan instantly second step
    qs = qs.exclude(suitable_for='veggie').filter(key__regex=r'(B|C|D|E|F|G|H|N|P|R)[0-9]')\
        .exclude(
        name__regex=not_veggie)
    print(qs)
    print('\n')
    with open('Output.txt', 'w', encoding="utf-8") as f:
        for item in qs.values_list('name', flat=True):
            print(item + '\n', file=f)

    qs.update(suitable_for='veggie')
    '''
    # more complex filtering
    qs_veggie = qs.exclude(suitable_for='veggie')
    print(qs_veggie)
    print(qs_veggie.count())
    print('\n')
    
    with open('Output.txt', 'w', encoding="utf-8") as f:
        for item in qs_veggie.values_list('name', flat=True):
            print(item + '\n', file=f)
    
    # exclude meats, fish, animal fats, gelatine
    qs_veggie = qs_veggie.exclude(key__regex=r'Q[7-8]|(T|U|V|W|Y)[0-9]')
    

    qs_veggie = qs_veggie.exclude(name__regex=not_veggie)
    print(qs_veggie)
    print(qs_veggie.count())
    with open('Output2.txt', 'w', encoding="utf-8") as f:
        for item in qs_veggie.values_list('name', flat=True):
            print(item + '\n', file=f)
    qs_veggie.update(suitable_for='veggie')


def set_contains():
    qs = Ingredient.objects.all()
    nuts = r'nuss|Nuss|nuesse|Nuesse|mandel|Mandel|pistazie|Pistazie|macadamia|Macadamia|pekan|Pekan|' \
           r'Baklava|Krokant|(m|M)arzipan|(n|N)ougat|(n|N)oisette|(k|K)okos|Florentiner'
    qs = qs.filter(name__regex=nuts)
    print(qs)
    print(qs.count())
    qs.update(contains='n')


def set_type():
    qs = Ingredient.objects.all()
    b = MealType.objects.get(name='breakfast')
    l = MealType.objects.get(name='lunch')
    d= MealType.objects.get(name='dinner')
    s = MealType.objects.get(name='snack')
    # brot, cerealien, eier, milch, kaese, joguhrt, quark, ... , aufstriche
    qs_b = qs.filter(key__regex=r'B|C|E1|M0|M1[1-4]|M[3-7]|M8[0-3]|M85[1-9]|M86[0-2]|M8A[2-9]|M8B[0-4]|M8C|S1[2-5]|S16[0-1]|S16[5-8]|W|X0')
    qs_d = qs.filter(key__regex=r'B|E1|M0|M1[1-4]|M[3-7]|M8[0-3]|M85[1-9]|M86[0-2]|M8A[2-9]|M8B[0-4]|M8C')
    b.mealtype.set(qs_b)
    #d.mealtype.set(qs)
    #l.mealtype.set(qs)
    #s.mealtype.set(qs)

def correct_vd_vb12():
    Ingredient.objects.update(portion_size=1)
    ingreds = Ingredient.objects.filter(vitamin_d__isnull=True)
    from decimal import Decimal
    file = open('vdv12.csv','r')
    for line in file:
        for key in ingreds.values_list('key',flat=True):
            l = line.split(';')
            if l[0] == key:
                i = ingreds.get(key=key)
                print(i)
                print(l[1])
                i.vitamin_d = Decimal(l[1])
                i.save()
    file.close()
    ingreds = Ingredient.objects.filter(vitamin_b12__isnull=True)
    file = open('vdv12.csv', 'r')
    for line in file:
        for key in ingreds.values_list('key', flat=True):
            l = line.split(';')
            if l[0] == key:
                i = ingreds.get(key=key)
                print(i)
                print(l[2])
                i.vitamin_b12 = Decimal(l[2])
                i.save()
    file.close()

def group_by_nutrients():
    import json
    letters = ['B','C','D','E','F','G','H','K','M','N','P','Q','R','S','T','U','V','W','X','Y']
    for l in letters:
        ingredients = Ingredient.objects.filter(status='relevant', key__startswith=l)
        result = {}
        print(l)
        for i in ingredients:
            same = ingredients.filter(carbs__lte=i.carbs+5000,carbs__gte=i.carbs-5000,
                                      protein__lte=i.protein+5000,protein__gte=i.protein-5000,
                                      fat__lte=i.fat+5000,fat__gte=i.fat-5000)
            print(same)
            #if i.key in result.keys() or i in result.values():
            #    continue
            #result[i.key] = same
            #ingredients = ingredients.exclude(key__in=list(same.values_list('key',flat=True)))

            i.similar_macros = json.dumps(list(same.values_list('key',flat=True)))
            i.save()
        #for groupkey in result:
        #    print(groupkey, result[groupkey])

def correct_DB():
    file = open('lappi_keys.txt','r')
    file2 = open('added_keys.txt','w')
    file2.write(' ')
    file2.close()
    file2 = open('added_keys.txt','a')
    ings = Ingredient.objects.all()
    for lines in file:
        line = lines.split(';')
        if ings.filter(key=line[1]).exists():
            continue
        else:
            print('#####CREATE#####')
            try:
                i = Ingredient(
                    key=line[1],
                    name=line[2],
                    suitable_for=line[3],
                    contains=line[4],
                    suitable_for_religion=line[5],
                    energy_kcal=line[6],
                    energy_kj=line[7],
                    fat=line[8],
                    protein=line[9],
                    fibre=line[10],
                    sugar_total=line[11],
                    sum_of_saturated_fatty_acids=line[12],
                    sum_of_monounsaturated_fatty_acids=line[13],
                    sum_of_polyunsaturated_fatty_acids=line[14],
                    lactose=line[15],
                    fructose=line[16],
                    vitamin_a=line[17],
                    vitamin_b1=line[18],
                    vitamin_b2=line[19],
                    vitamin_b3=line[20],
                    vitamin_b5=line[21],
                    vitamin_b6=line[22],
                    vitamin_b7=line[23],
                    vitamin_b9=line[24],
                    vitamin_b12=line[25],
                    vitamin_c=line[26],
                    vitamin_d=line[27],
                    vitamin_e=line[28],
                    vitamin_k=line[29],
                    sodium=line[30],
                    potassium=line[31],
                    calcium=line[32],
                    magnesium=line[33],
                    phosphorus=line[34],
                    sulphur=line[35],
                    chloride=line[36],
                    iron=line[37],
                    zinc=line[38],
                    copper=line[39],
                    manganese=line[40],
                    fluoride=line[41],
                    iodide=line[42],
                    portion_size=0.0,
                    status=line[44],
                    similar_macros=line[45]
                    )
                i.save()
                l = ''+str(i.key)+'\n'
            except IndexError:
                print('list out of bounds')
                
                l = lines+'\n'
            file2.write(str(l))
    file2.close()
    file.close()
    '''
    H130000
    H510900
    K260262
    K280200
    K310222
    K391282
    F553400
    F572000
    G542182
    '''

def portionsgroessen():
    file = open('portionsgrgoessen.csv','r')
    ingreds = Ingredient.objects.all()
    for line in file:
        l = line.split(';')
        i = ingreds.filter(key=l[0])
        if i:
            i[0].standard_portion_size = l[2]
            i[0].save()
    file.close()

def portionsgroessen2():
    ingreds = Ingredient.objects.all()
    for i in ingreds:
        i.standard_portion_size = i.standard_portion_size/100
        i.save()



def countIngreds():
    meals = Meal.objects.all()
    food_list = ''
    for m in meals:
        for i in m.ingredients.all():
            food_list += i.name + ' '
    counts = dict()
    words = food_list.split(' ')
    for word in words:
        if word.islower():
            continue
        if word in counts:
          counts[word] += 1
        else:
          counts[word] = 1
    sorted_x = sorted(counts.items(), key=lambda kv: kv[1])
    return sorted_x