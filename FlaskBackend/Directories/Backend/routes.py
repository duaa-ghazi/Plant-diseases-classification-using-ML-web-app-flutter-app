import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as img
from keras.preprocessing.image import img_to_array
import numpy as np
import tensorflow as tf
from datetime import datetime
from flask import Flask,Blueprint,request,render_template,jsonify
from tensorflow.python.keras.backend import switch

from Directories.Database import collection as db
from keras.optimizers import SGD
from flask import Flask, render_template, jsonify
import json


mod = Blueprint('backend',__name__,template_folder='templates',static_folder='./static')
UPLOAD_URL = 'http://192.168.1.77:5000/static/'

list_of_classes=['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust',
                 'Apple___healthy', 'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew',
                 'Cherry_(including_sour)___healthy', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
                 'Corn_(maize)___Common_rust_', 'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy',
                 'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
                 'Grape___healthy', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot',
                 'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight',
                 'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy',
                 'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy', 'Tomato___Bacterial_spot',
                 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot',
                 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot',
                 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy']

ResNet50_Model= load_model("Directories/TrainedModels/Pre_Resnet50.h5")
ResNet50_Model.compile(loss='categorical_crossentropy',
            optimizer=tf.keras.optimizers.Adam(lr=1e-4),
            metrics=['accuracy'])


AlexNet_Model= load_model("Directories/TrainedModels/AlexNet.h5")
opt = tf.keras.optimizers.Adam(lr=1e-4, decay=1e-6)
AlexNet_Model.compile(loss="binary_crossentropy", optimizer=opt, metrics=["accuracy"])


InceptionV3_Model=load_model("Directories/TrainedModels/INC_V3_Pre.hdf5")
InceptionV3_Model.compile(optimizer=SGD(lr=0.0001, momentum=0.9), loss='categorical_crossentropy', metrics=['accuracy'])


VGG16_Model=load_model("Directories/TrainedModels/VGG_2_Pre.hdf5")
opt = tf.keras.optimizers.Adam(lr = 1e-4, decay = 1e-6)
VGG16_Model.compile(loss="categorical_crossentropy", optimizer = opt,metrics = ["accuracy"])



@mod.route('/')
def home():
    
    return render_template('index.html')



@mod.route('/predict' ,methods=['POST'])
def predict():  
     if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
           return "something went wrong 1"

        user_file = request.files['file']

        if user_file.filename == '':

            return "file name not found ..." 
       
        else:

            x = user_file.filename.split("&")
            if len(x)==1:
                user_uid="from-computer"
            else:
                user_uid = x[1]
            path = os.path.join(os.getcwd()+'\\Directories\\static\\'+x[0])
            user_file.save(path)
            class_name,img_prob,model_name = identifyImage(path)

            information = getInformation(str(class_name))

            db.addNewImage(
                user_uid,
                x[0],
                str(img_prob),
                str(class_name),
                str(model_name),
                datetime.now(),
                UPLOAD_URL+x[0],
                str(information))

            result={
                    "status":"success",
                    "prediction":str(img_prob),
                    "confidence":str(class_name),
                    "upload_time":datetime.now(),
                    "url": UPLOAD_URL+x[0],


                    }
            if user_uid=="from-computer":
                return render_template('index2.html',data=result)
            else :
                return jsonify({
                    "status": "success",
                    "prediction": str(img_prob),
                    "confidence": str(class_name),
                    "model_name": str(model_name),
                    "upload_time": datetime.now(),
                    "information": str(information),
                })


def identifyImage(img_path):
   
    image_M1 = img.load_img(img_path,target_size=(224, 224))
    x1 = img_to_array(image_M1)
    x1 = np.expand_dims(x1, axis=0)
    x1 = x1 / 255

    ResNet50_Model_preds = ResNet50_Model.predict(x1)
    d1 = ResNet50_Model_preds.flatten()
    j1 = d1.max()
    for index1, item1 in enumerate(d1):
        if item1 == j1:
            ResNet50_Model_class_name = list_of_classes[index1]
    ResNet50_Model_img_prob = j1*100
    print("cutum model result using Resnet ")
    print(ResNet50_Model_class_name)
    print(ResNet50_Model_img_prob)
    print("/////////")
#******************************************
    image_M2 = img.load_img(img_path,target_size=(227, 227))
    x2 = img_to_array(image_M2 )
    x2 = np.expand_dims(x2, axis=0)
    x2 = x2 / 255

    AlexNet_Model_preds = AlexNet_Model.predict(x2)
    d2 = AlexNet_Model_preds.flatten()
    j2 = d2.max()
    for index2, item2 in enumerate(d2):
        if item2 == j2:
            AlexNet_Model_class_name = list_of_classes[index2]
    AlexNet_Model_img_prob = j2*100
    print(" cutum model result using AlexNet ")
    print(AlexNet_Model_class_name)
    print(AlexNet_Model_img_prob)
    print("/////////")
# ******************************************
    image_M3 = img.load_img(img_path,target_size=(299, 299))
    x3 = img_to_array(image_M3)
    x3 = np.expand_dims(x3, axis=0)
    x3 = x3 / 255

    InceptionV3_Model_preds = InceptionV3_Model.predict(x3)
    d3 = InceptionV3_Model_preds.flatten()
    j3= d3.max()
    for index3, item3 in enumerate(d3):
        if item3 == j3:
            InceptionV3_Model_class_name = list_of_classes[index3]
    InceptionV3_Model_img_prob = j3*100
    print("cutum model result using inceptionV3 ")
    print(InceptionV3_Model_class_name)
    print(InceptionV3_Model_img_prob)
    print("/////////")
# ******************************************
    image_M4 = img.load_img(img_path,target_size=(224, 224))
    x4 = img_to_array(image_M4 )
    x4 = np.expand_dims(x4, axis=0)
    x4 = x4/ 255

    VGG16_Model_preds = VGG16_Model.predict(x4)
    d4 = VGG16_Model_preds.flatten()
    j4 = d4.max()
    for index4, item4 in enumerate(d4):
        if item4 == j4:
            VGG16_Model_class_name = list_of_classes[index4]
    VGG16_Model_img_prob = j4*100
    print("cutum model result using VGG16 ")
    print(VGG16_Model_class_name)
    print(VGG16_Model_img_prob)
    print("/////////")

    max_value=0.0000000000

    list_of_predictions = [ResNet50_Model_img_prob, AlexNet_Model_img_prob, InceptionV3_Model_img_prob, VGG16_Model_img_prob]
    for i in range(4):
        if list_of_predictions[i] > max_value:
            max_value = list_of_predictions[i]




    if  max_value==ResNet50_Model_img_prob:
        class_name=ResNet50_Model_class_name
        img_prob =ResNet50_Model_img_prob
        model_name="ResNet50_Model"

    elif max_value==AlexNet_Model_img_prob:
        class_name=AlexNet_Model_class_name
        img_prob =AlexNet_Model_img_prob
        model_name="AlexNet_Model"

    elif max_value==InceptionV3_Model_img_prob:
        class_name=InceptionV3_Model_class_name
        img_prob =InceptionV3_Model_img_prob
        model_name="InceptionV3_Model"

    else:
        class_name=VGG16_Model_class_name
        img_prob =VGG16_Model_img_prob
        model_name="VGG16_Model"

    return  class_name,img_prob ,model_name
            

   


def getInformation(  class_name):
    switcher = {
       "Apple___Apple_scab" : """Apple_scab is a serious disease of apples and ornamental crabapples, apple scab (Venturia inaequalis) attacks both leaves and fruit. The fungal disease forms pale yellow or
olive-green spots on the upper surface of leaves. Dark, velvety spots may appear on the lower surface. Severely infected leaves become twisted and puckered and may
drop early in the summer.
                    
Environment :
Apple scab overwinters primarily in fallen leaves and in the soil. Disease development is favored by wet,cool weather that generally occurs in spring and early summer.
Fungal spores are carried by wind, rain or splashing water from the ground to flowers, leaves or fruit. During damp or rainy periods, newly opening apple leaves are
extremely susceptible to infection. The longer the leaves remain wet, the more severe the infection will be. Apple scab spreads rapidly between 55-75 degrees F.
    
Treatment :
1)Choose resistant varieties when possible.
2)Rake under trees and destroy infected leaves to reduce the number of fungal spores available to start the disease cycle over again next spring.
3)Water in the evening or early morning hours (avoid overhead irrigation) to give the leaves time to dry out before infection can occur.
4)Spread a 3- to 6-inch layer of compost under trees, keeping it away from the trunk, to cover soil and prevent splash dispersal of the fungal spores.
5)For best control, spray liquid copper soap early, two weeks before symptoms normally appear. Alternatively, begin applications when disease first appears,
  and repeat at 7 to 10 day intervals up to blossom drop.""" ,

      "Apple___Black_rot":""" Black rot is a disease of apples that infects fruit, leaves and bark caused by the fungus Botryosphaeria obtusa.Although trees of all ages can be
infected, most trees that die from black root rot are at least 10 years old.
Begin checking your apple trees for signs of infection about a week after the petals fall from your apple blossoms. Early symptoms are often limited to leaf symptoms
such as purple spots on upper leaf surfaces. As these spots age, the margins remain purple, but the centers dry out and turn yellow to brown. Over time, the spots 
expand and heavily infected leaves drop from the tree.
                    
Environment :
Rains result in thousands of conidia oozing out of the diseased tissue. Splashing rain, insects, and wind all serve to spread the spores to cause new infections.
Temperature has an enormous effect on whether infection will occur. If the temperature is between 61 and 90 F, both conidia and ascospores can germinate in four hours.
Eighty degrees F is the optimal temperature for the leaves to get infected. In contrast, for fruit infection to occur, the temperatures must be in the range of 68 to
75 F during a wetting period of at least nine hours.
                    
Treatment :
1)Treating black rot on apple trees starts with sanitation. Because fungal spores overwinter on fallen leaves, mummified fruits, dead bark and cankers, it’s important 
  to keep all the fallen debris and dead fruit cleaned up and away from the tree.
2)During the winter, check for red cankers and remove them by cutting them out or pruning away the affected limbs at least six inches beyond the wound.
  Destroy all infected tissue immediately and keep a watchful eye out for new signs of infection.
3)Once black rot disease is under control in your tree and you’re again harvesting healthy fruits, make sure to remove any injured or insect-invaded fruits to avoid 
  re-infection. Although general purpose fungicides, like copper-based sprays and lime sulfur, can be used to control black rot, nothing will improve apple black rot 
  like removing all sources of spores.""",

        "Apple___Cedar_apple_rust" :"""is a fungal disease that requires juniper plants to complete its complicated two year life-cycle. Spores overwinter as a reddish-brown gall on young twigs of various
juniper species. In early spring, during wet weather, these galls swell and bright orange masses of spores are blown by the wind where they infect susceptible apple
and crab-apple trees. The spores that develop on these trees will only infect junipers the following year. From year to year, the disease must pass from junipers to 
apples to junipers again; it cannot spread between apple trees.
                     
Environment :
This disease require plants from two different families in order to complete their life cycle; one plant from the (red cedar, juniper) and the other from 
the(crabapple, hawthorn, serviceberry). 
                    
Treatment :
1)Choose resistant cultivars when available.
2)Rake up and dispose of fallen leaves and other debris from under trees.
3)Remove galls from infected junipers. In some cases, juniper plants should be removed entirely.
4)Apply preventative, disease-fighting fungicides labeled for use on apples weekly, starting with bud break, to protect trees from spores being released by the juniper
  host. This occurs only once per year, so additional applications after this springtime spread are not necessary.
5)On juniper, rust can be controlled by spraying plants with a copper solution (0.5 to 2.0 oz/ gallon of water) at least four times between late August and late
  October.""",

        "Apple___healthy" :"No information needed , it is healty",

         "Blueberry___healthy":"No information needed , it is healty",

        "Cherry_(including_sour)___Powdery_mildew":"""Powdery mildew of sweet and sour cherry is caused by Podosphaera clandestina, an obligate biotrophic fungus. Mid- and late-season sweet cherry cultivars are commonly
affected, rendering them unmarketable due to the covering of white fungal growth on the cherry surface . Season long disease control of both leaves and fruit
is critical to minimize overall disease pressure in the orchard and consequently to protect developing fruit from accumulating spores on their surfaces.
                    
Environment :
It is important to know when cherry powdery mildew is active because often growers only manage the disease during the cherry fruit growing
season. Continue management during the full fungal growing season which continues through late summer and early fall.
Typically, it takes 1/10th of an inch of rain or irrigation and temperatures of 50°F or more for spring primary infections to occur.
The fungus does not need free water to thrive. High humidity and temperatures of 70°F to 80°F favor the disease. Spore dispersal is diurnal, with spore concentrations
peaking late morning to early afternoon.

Treatment :
Treat it early by cutting off an infected branch at a point below the gall, and applying fungicides three times annually: in spring, just before flowering and just 
after. Fungicide application is also the treatment of choice for brown rot and leaf spot. Shriveled fruit covered with spores indicates brown rot, while purple or 
brown circles on leaves signal leaf spot. For brown rot, apply the fungicide when buds emerge and again when the tree is 90 percent in bloom.
""",
        'Cherry_(including_sour)___healthy':"No information needed , it is healty",

        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot':"""Grey leaf spot is a foliar fungal disease that affects maize,  GLS is considered one of the most significant yield-limiting diseases of corn worldwide. 
Symptoms seen on corn include leaf lesions, discoloration (chlorosis), and foliar blight. Distinct symptoms of GLS are rectangular, brown to gray necrotic lesions 
that run parallel to the leaf, spanning the spaces between the secondary leaf veins. 
                    
Environment :
The fungus survives in the debris of topsoil and infects healthy crop via asexual spores called conidia. Environmental conditions that best suit infection and growth 
include moist, humid, and warm climates. Poor airflow, low sunlight, overcrowding, improper soil nutrient and irrigation management, and poor soil drainage can all 
contribute to the propagation of the disease. Management techniques include crop resistance, crop rotation, residue management, use of fungicides, and weed control.
                    
Treatment :
1)Reduce thatch layer.
2)Irrigate deeply, but infrequently. This generally means one time per week with one inch of water. Always irrigate in the morning, which promotes quick drying of the
  foliage.
3)Avoid using post-emergent weed killers on the lawn while the disease is active.
4)Avoid medium to high nitrogen fertilizer levels.
5)Improve air circulation and light level on lawn. Limb up over-hanging trees and prune back nearby shrubs.
6)Mow at the proper height and only mow when the grass is dry. Bag and dispose of grass clippings if disease is present.
7)Control chinch bug infestations.
8)Use fungicide treatments as needed along with proper turfgrass culture.""",

        'Corn_(maize)___Common_rust_':"""Common rust on sweet corn is caused by the fungus Puccinia sorghi. Epidemics of this disease can cause serious losses in yield and quality of sweet corn. High rust 
susceptibility of many popular sweet corn hybrids is a major factor contributing to rust epidemics. Another factor is that sweet corn is usually planted over an
extended period from May through June for fresh and processing uses.
                    
Environment :
Young leaves are most susceptible to infection and pustules are more likely to form after corn silking. The disease favors cool temperatures (60 - 76 degrees F),
heavy dews, about six hours of leaf wetness, and relative humidity greater than 95 percent. Temperatures above 80 degrees F suppress disease development and spread.
                    
Treatment :
The best management practice is to use resistant corn hybrids. Fungicides can also be beneficial, especially if applied early when few pustules have appeared on 
the leaves.""",

        'Corn_(maize)___Northern_Leaf_Blight':"""Northern corn leaf blight caused by the fungus Exerohilum turcicum is a common leaf blight is favored by wet humid cool weather typically found later in the growing
season.Spores of the fungus that causes this disease can be transported by wind long distances from infected fields.
                    
Environment :
The ideal environment for it occurs during relatively cool, wet seasons. Periods of wetness that last more than six hours at temperatures between 18 and 27 °C 
are most conducive to disease development. Infection is inhibited by high light intensity and warm temperatures. Leaving large amounts of infected residue exposed
in the field and continuing to plant corn in those fields will promote disease progress by providing large amounts of inoculum early in the season.Also, the number of 
conidia produced in an infected field increases significantly after rain due to the increase in moisture.
                    
Treatment :
Control of this disease is often focused on management and prevention. First, choose corn varieties or hybrids that are resistant or at least have moderate resistance 
to northern corn leaf blight. When you grow corn, make sure it does not stay wet for long periods of time. The fungus that causes this infection needs between six and
18 hours of leaf wetness to develop. Plant corn with enough space for airflow and water in the morning so leaves can dry throughout the day.Tilling the corn into the 
soil is one strategy, but with a small garden it may make more sense to just remove and destroy the affected plants. Treating northern corn leaf blight involves using 
fungicides. For most home gardeners this step isn’t needed, but if you have a bad infection, you may want to try this chemical treatment
""",

        'Corn_(maize)___healthy':"No information needed , it is healty",

        'Grape___Black_rot':"""Black rot of grapes is a fungal disease that persists in grapevines for many years without treatment. The earliest signs of disease appear as yellow circular lesions
on young leaves. As these lesions spread, they brown and sprout black fungal fruiting bodies that look similar to grains of pepper. With advancing disease, lesions
may girdle the petiole of individual leaves, killing them. Eventually, the fungus spreads to the shoots, causing large black elliptical lesions.
                    
Environment :
When the weather is moist, ascospores are produced and released throughout the entire spring and summer, providing continuous primary infection. The black rot fungus
requires warm weather for optimal growth; cool weather slows its growth. A period of two to three days of rain.
                    
Treatment :
Grape black rot is difficult to stop once it has taken hold of growing fruit.Many gardeners would consider this year’s crop a lost cause and work toward preventing a
recurrence of disease. The best time to treat black rot of grapes is between bud break until about four weeks after bloom.
""",

        'Grape___Esca_(Black_Measles)':"""Grapevine measles, also called esca, black measles or Spanish measles, has long plagued grape growers with its cryptic expression of symptoms and, for a long time,
a lack of identifiable causal organism(s). The name ‘measles’ refers to the superficial spots found on the fruit . During the season, the spots may coalesce over the
skin surface, making berries black in appearance. 
                    
Environment :
Symptoms first become apparent in vineyards 5 to 7 or more years old, but the infections actually occur in younger vines. The overwintering structures that produce 
spores  are embedded in diseased woody parts of vines. During fall to spring rainfall, spores are released and wounds made by dormant pruning provide infection sites.
Wounds may remain susceptible to infection for several weeks after pruning with susceptibility declining over time. 
                    
Treatment :
Presently, there are no effective management strategies for measles. Raisins affected by measles will be discarded during harvest or at the packing house, while table
grape growers will leave affected fruit on the vine. Current research is focused on protecting pruning wounds from fungal infections to minimize suspect fungi from
colonizing fresh wounds.""",

        'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)':"""Leaf spots are round blemishes found on the leaves of many species of plants, mostly caused by parasitic fungi or bacteria.
A typical spot is "zonal", meaning it has a definite edge and often has a darker border. When many spots are present, they can grow together and become a blight or 
a blotch. Fungal spots are usually round or free-form in shape.
                    
Environment :
The disease occurs in late spring and summer and appears to be enhanced by soil moisture fluctuations, especially drought stress caused by watering restrictions and 
poor irrigation system coverage. However, the disease may also develop during periods of hot weather preceded by unusually wet soil conditions caused by excessive rain
or over-irrigation. 
                    
Treatment :
1)Reduce thatch and promote water penetration through the soil by yearly aerification. Maintain grass height between 2 ½ and 3 inches. Minimize wounding of the leaf
  blades by maintaining sharp mower blades.
2)Avoid excessive applications of nitrogen fertilizer, especially in spring. This promotes rapid, succulent leaf growth that requires more frequent mowing.
3)Try to maintain uniform soil moisture. Check the irrigation system to make sure all irrigation heads are working properly and that water is being distributed 
  uniformly to avoid drought stress. On the other hand excessive irrigation and poorly drained soils may also promote disease development.""",

        'Grape___healthy':"No information needed , it is healty",

        'Orange___Haunglongbing_(Citrus_greening)':"""is a disease of citrus caused by a vector-transmitted pathogen. The causative agents are motile bacteria,the disease is vectored.distinguished by the common symptoms
of yellowing of the veins and adjacent tissues; followed by splotchy mottling of the entire leaf, premature defoliation, dieback of twigs, decay of feeder rootlets
and lateral roots, and decline in vigor, ultimately followed by the death of the entire plant.  
                    
Environment :
Because citrus greening transmission depends on temperature environmental conditions affect transmission and in turn concluded recommendations for implementing 
surveillance and prevention practices.
The model estimates that host plants are the most vulnerable when temperatures are between 16 and 33 degrees Celsius, though the sweet spot for transmission hovers
at around 25 degrees Celsius. 
                    
Treatment :
1)Advanced Nutritional Supplements:Providing better nutrition helps trees fight against citrus greening and enables them to continue to produce quality fruit.
2)Reflective Mulch:This has proven to be successful with certain vegetable crops and is continuing to be explored in preventing new citrus trees from being infected.
3)Heat Treatment: Heating HLB-infected trees in the sun by encasing them in plastic “tents” slows or diminishes the psyllid count, which may potentially prolong 
the productivity of trees. 
""",

        'Peach___Bacterial_spot':"""Bacterial spot is an important disease of peaches, caused by Xanthomonas campestris. Symptoms of this disease include fruit spots, leaf spots, and twig cankers. 
Fruit symptoms include pitting, cracking, gumming, and watersoaked tissue, which can make the fruit more susceptible to brown rot, rhizopus, and other fungal 
infections. Severe leaf spot infections can cause early defoliation. Severe defoliation can result in reduced fruit size, and sunburn and cracking of fruit.
                    
Environment :
Bacterial spot is favored by hot, dewy, wet conditions, and windy, sandy sites. Spread and entry of the bacterial spot pathogen into plants is favored by abrasions
and nicks caused by blowing sand, especially common on outside peach rows next to dirt roads. Spraying trees when foliage is wet from rain or dew may help to spread 
bacterial spot.
                    
Treatment :
Keep your peach trees healthy by properly pruning out any diseased or dead limbs and fertilize and water as necessary. Too much nitrogen can aggravate the disease.
While there are no completely successful sprays for control of this disease, chemical spray with copper based bactericide and the antibiotic oxytetracycline have
some effect used preventatively. Talk to your local extension office or nursery for information. Chemical control is doubtful, however, so the best long term control
is to plant resistant cultivars.""",

        'Peach___healthy':"No information needed , it is healty",

        'Pepper,_bell___Bacterial_spot':"""Leaf spots that appear on the lower surface of older leaves as small, pimples and on the upper leaf surface as small water-soaked spots are a symptom of bacterial spot.
This is an important pepper disease It also occasionally attacks tomatoes. Eventually, the spots develop gray to tan centers with darker borders. 
                    
Environment :
Lesions enlarge during warm, humid weather. Leaves may then turn yellow, then brown and drop. Lesions may also develop on stems. Fruits develop small, raised rough spots that do not
affect eating quality. Severely infected leaves will drop resulting in sunscald of peppers. Bacterial leaf spot is spread by splashing rain and working with wet, 
infected plants. This disease can defoliate plants during wet weather. Hot, dry weather slows the spread of this disease. The disease can come in on seed or
transplants and can overwinter in crop residue and soil.
                    
Treatment :
1)Select resistant varieties
2)Purchase disease-free seed and transplants.
3)Treat seeds by soaking them for 2 minutes in a 10% chlorine bleach solution (1 part bleach; 9 parts water). Thoroughly rinse seeds and dry them before planting.
4)Mulch plants deeply with a thick organic material like newspaper covered with straw or grass clippings.
5)Avoid overhead watering.
6)Remove and discard badly infected plant parts and all debris at the end of the season.
7)Spray every 10-14 days with fixed copper (organic fungicide) to slow down the spread of infection.
8)Rotate peppers to a different location if infections are severe and cover the soil with black plastic mulch or black landscape fabric prior to planting.""",

        'Pepper,_bell___healthy':"No information needed , it is healty ",

        'Potato___Early_blight':"""Early blight of potato is caused by the fungal pathogen Alternaria solani. The disease affects leaves, stems and tubers and can reduce yield, tuber size,
storability of tubers, quality of fresh-market and processing tubers and marketability of the crop.
                    
Environment :
in most production areas, early blight occurs annually to some degree. The severity of early blight is dependent upon the frequency of foliar wetness from rain,
dew, or irrigation; the nutritional status of the foliage; and cultivar susceptibility.
                    
Treatment :
1)Select a late-season variety with a lower susceptibility to early blight. (Resistance is associated with plant maturity and early maturing cultivars are more 
  susceptible).
2)Time irrigation to minimize leaf wetness duration during cloudy weather and allow sufficient time for leaves to dry prior to nightfall.
3)Avoid nitrogen and phosphorus deficiency.
4)Pay particular attention to edges of fields that are adjacent to fields planted to potato the previous year.
5)Rotate foliar fungicides.""",

        'Potato___Late_blight':"""Late blight is caused by the funguslike oomycete pathogen Phytophthora infestans. This potentially devastating disease can infect potato foliage and tubers at any
stage of crop development. 
                    
Environment :
during cool, moist weather, these lesions expand rapidly into large, dark brown or black lesions, often appearing greasy .
                    
Treatment :
1)Destroy all cull and volunteer potatoes.
2)Plant late blight-free seed tubers.
3)Do not mix seed lots because cutting can transmit late blight
4)Avoid planting problem areas that may remain wet for extended periods or may be difficult to spray .
5)Avoid excessive and/or nighttime irrigation.
6)Eliminate sources of inoculum such as hairy nightshade weed species and volunteer potatoes.
""",

        'Potato___healthy':"No information needed , it is healty ",

        'Raspberry___healthy':"No information needed , it is healty ",

        'Soybean___healthy':"No information needed , it is healty",

        'Squash___Powdery_mildew':"""Powdery mildew, mainly caused by the fungus Podosphaera xanthii, infects all cucurbits, including muskmelons, squash, cucumbers, gourds, watermelons and pumpkins. 
In severe cases, powdery mildew can cause premature death of leaves, and reduce yield and fruit quality.
                    
Environment :
Powdery mildew infections favor humid conditions with temperatures around 68-81° F.
In warm, dry conditions, new spores form and easily spread the disease.
                    
Treatment :
1)Plant varieties with complete or partial resistance to powdery mildew.
2)Apply fertilizer based on soil test results. Avoid over-applying nitrogen.
3)Provide good air movement around plants through proper spacing, staking of plants and weed control.
4)Home gardeners can apply sulfur products to both the upper and lower surface of the leaves.
5)Commercial growers should refer to the Midwest Vegetable Production Guide for pesticide recommendations.
""",

        'Strawberry___Leaf_scorch':"""Scorched strawberry leaves are caused by a fungal infection which affects the foliage of strawberry plantings. The fungus responsible is called Diplocarpon earliana.
Strawberries with leaf scorch may first show signs of issue with the development of small purplish blemishes that occur on the topside of leaves.
                    
Environment :
Leaf scorch can infect strawberry leaves at all stages of development.  Most infections take place in early spring, or mid-August to late September- 
when most leaves are young and frequent rains or heavy dews provide good conditions for infection.  The optimal temperature for germination occurs between 20 and 25°C
but germination can occur at temperatures between 5°C and 30°C (41- 86°F) with a sufficient wetting period (at least 6- 9 hours).  
Symptoms appear within 7- 9 days after infection and spores are produced within 10- 14 days
                    
Treatment :
1)When dry weather conditions occur over an extended period of time, plants should receive deep supplemental watering every 10 to 14 days.
  Newly transplanted trees and shrubs should be watered every 7 to 10 days. A slow soaking of the soil is most effective.
2)Conserve soil moisture by mulching plants with a 3-4" depth of organic mulch, such as woodchips, leaf mold, or bark. Because mulches absorb water from the surface,
  be sure to water thoroughly so water penetrates into the soil.
3)Keep lawn fetilizers outside of the dripline of trees and shrubs.
4)Prune any dead, diseased, or crossing branches to reduce the amount of foliage the root system must support.
""",

        'Strawberry___healthy':"No information needed , it is healty",

        'Tomato___Bacterial_spot':"""Bacterial spot is caused by four species of Xanthomonas and occurs worldwide wherever tomatoes are grown. Bacterial spot causes leaf and fruit spots,
which leads to defoliation, sun-scalded fruit, and yield loss.Due to diversity within the bacterial spot pathogens.
                    
Environment :
the disease can occur at different temperatures and is a threat to tomato production worldwide. Disease development is favored by temperatures of 75 to 86 ℉ and
high precipitation. it is more prevalent in seasons with high precipitation and less prevalent during dry years.
                    
Treatment :
1)The most effective management strategy is the use of pathogen-free certified seeds and disease-free transplants to prevent the introduction of the pathogen into 
  greenhouses and field production areas. Inspect plants very carefully and reject infected transplants- including your own!
2)In the greenhouse, discard trays adjacent to outbreak location to minimize disease spread.
3)In transplant production greenhouses, minimize overwatering and handling of seedlings when they are wet.
4)Trays, benches, tools, and greenhouse structures should be washed and sanitized between seedlings crops.
5)Eliminate solanaceous weeds in and around tomato and pepper production areas.
6)Keep cull piles away from field operations.
7)Do not spray, tie, harvest, or handle wet plants as that can spread the disease.
""",

         'Tomato___Early_blight':"""Early blight is one of the most common tomato diseases, occurring nearly every season wherever tomatoes are grown.
It affects leaves, fruits and stems and can be severely yield limiting when susceptible cultivars are used and weather is favorable.
Severe defoliation can occur and result in sunscald on the fruit.
                    
Environment :
Disease develops at moderate to warm (59 to 80 F) temperatures; 82 to 86 F optimum
Rainy weather or heavy dew, 90% humidity or greater
                    
Treatment :
1)Remove all garden crop residue; a thorough cleanup is essential
2)Rotate crops when possible
3)Space plants apart for good air circulation; no closer than 3 feet
4)Water the soil around the plants in the morning only; No overhead watering. Don’t put your plants to sleep with wet feet!
5)Control insects. Aphids and White flies can spread diseases
6)Remove weeds that may attract insects
7)Don’t work in a wet garden
8)Maintain a fertilization schedule.""",

        'Tomato___Late_blight': """is a potentially devastating disease of tomato and potato, infecting leaves, stems and fruits of tomato plants.
The disease spreads quickly in fields and can result in total crop failure if untreated.
        
Environment :
Spreads most in cool (60°F to 70°F), damp weather.
Prolonged hot dry days can halt pathogen spread.
        
Treatment :
1) Choose the right variety.
2) Prevent overwintering.
3) Give plants space.
4) Avoid watering from above.
5) Pay attention to the weather:
  Learn to recognize the weather conditions that foster the spread of late blight. The disease spreads rapidly in cool wet weather,
whereas dry weather tends to hold back the disease. The USA Blight website tracks the occurence of late blight in real time.
Check the site regularly during the growing season. Your local cooperative extension may be a good source of information, too.
Stay in touch with gardeners in your area so you'll know right away if late blight is near. When late blight is detected in your
region, consider preventative spraying.""",

        'Tomato___Leaf_Mold':"""Leaf mold is not normally a problem in field-grown tomatoes in northern climates. 
It can cause losses in tomatoes grown in greenhouses or high tunnels due to the higher humidity found in these environments.
Foliage is often the only part of the plant infected and will cause infected leaves to wither and die, indirectly affecting yield.
In severe cases, blossoms and fruit can also be infected, directly reducing yield.
                    
Environment :
Optimal growth is at relative humidity greater than 85%.
Optimal temperature is between 71 °F and 75 °F, but disease can occur at temperatures as low as 50 °F and as high as 90 °F.
                    
Treatment :
1)Ensure there is enough spacing between your plants to provide enough airflow around all parts of the plant.
2)Don’t over fertilize your plants. New growth tends to be very susceptible to powdery mildew development.
3)Put plants where they will get enough light and avoid overly shady locations.
4)Make sure the soil can drain properly. Inadequate drainage can make soil a breeding ground for disease-causing organisms.
5)Keep plants properly maintained by removing any dead or diseased foliage and stems.
""",

        'Tomato___Septoria_leaf_spot':"""is a very common disease of tomatoes. It is caused by a fungus and can affect tomatoes and other plants , especially potatoes, just about anywhere in the world.
Although Septoria leaf spot is not necessarily fatal for your tomato plants, it spreads rapidly and can quickly defoliate and weaken the plants, rendering them 
unable to bear fruit to maturity.  
                    
Environment :
Is particularly severe in areas where wet, humid weather persists for extended periods.
                    
Treatment :
1)Remove diseased leaves. 
2)Improve air circulation around the plants.
3)Do not use overhead watering.
4)Control weeds.
5)Use crop rotation.
""",

        'Tomato___Spider_mites Two-spotted_spider_mite':"""The two-spotted spider mite is the most common mite species that attacks vegetable and fruit crops. Spider mites can occur in tomato. Two-spotted spider mites are one
of the most important pests of eggplant. They have up to 20 generations per year and are favored by excess nitrogen and dry and dusty conditions. Outbreaks are often
caused by the use of broad-spectrum insecticides which interfere with the numerous natural enemies that help to manage mite populations. As with most pests, catching
the problem early will mean easier control.
                    
Environment :
Two-spotted spider mites prefer hot (greater than 80° F), dry (less that 50% relative humidity) environmental conditions.
Two-spotted spider mites prefer to feed on leaf undersides. They use their stylet-like mouthparts to feed within individual plant cells, 
damaging the spongy mesophyll, palisade parenchyma and chloroplasts
                    
Treatment :
1)Avoid weedy fields and do not plant eggplant adjacent to legume forage crops.
2)Avoid early season, broad-spectrum insecticide applications for other pests.
3)Do not over-fertilize.
4)Overhead irrigation or prolonged periods of rain can help reduce populations.
""",

        'Tomato___Target_Spot':"""target spot of tomato is a fungal disease that attacks a diverse assortment of plants, as well as passion flower and certain ornamentals. Target spot on tomato fruit 
is difficult to control because the spores, which survive on plant refuse in the soil, are carried over from season to season. 
                    
Environment :
Target spot of tomato is favored by temperatures of 68 to 82°F and leaf wetness periods as long as 16 hours. The target spot fungus can survive in host residue
for a period. Therefore, it is possible that the target spot fungus could overwinter and cause disease during warm,
                    
Treatment :
1)Do not plant new crops next to older ones that have the disease.
2)Plant as far as possible from papaya, especially if leaves have small angular spots (Photo 5).
3)Check all seedlings in the nursery, and throw away any with leaf spots. 
4)Remove a few branches from the lower part of the plants to allow better airflow at the base
5)Remove and burn the lower leaves as soon as the disease is seen, especially after the lower fruit trusses have been picked.
6)Keep plots free from weeds, as some may be hosts of the fungus.
7)Do not use overhead irrigation; otherwise, it will create conditions for spore production and infection.
""",

        'Tomato___Tomato_Yellow_Leaf_Curl_Virus':"""Tomato yellow leaf curl virus is a DNA virus from the genus Begomovirus. It causes the most destructive disease of tomato, and it can be found in tropical and
subtropical regions causing severe economic losses. This virus is transmitted by an insect vector , commonly known as the silverleaf whitefly.  
                    
Environment :
when tomatoes grown in the field in the spring and summer, are exposed to high temperatures (40 oC and higher), often in combination with Tomato yellow leaf curl 
virus infection. 
                    
Treatment :
1)Use resistant or tolerant cultivars.
2)Protect seedlings from whiteflies.
3)Use only good seeds and healthy transplants.
4)Control whiteflies.
5)Immediately remove infected-looking plants and bury them.
6)Control weeds.
7)Do not plant cotton near tomato and/or other crops susceptible to whiteflies or vice versa.
8)Plow-under all plant debris after harvest or burn them when possible.
9)Practice crop rotation by planting crops that are not susceptible to whitefly.
""",

        'Tomato___Tomato_mosaic_virus':"""ToMV infects tomato most commonly, but the virus can also infect pepper, potato, apple, pear, cherry and numerous weeds.
Symptoms may differ on different hosts.ToMV has a very wide host range , Overall, tomato mosaic virus symptoms can be varied and hard to distinguish from 
other common tomato viruses. A definitive diagnosis can be accomplished by submitting a sample to Plant Disease Clinic.
                    
Environment :
Symptoms may be suppressed during cool temperatures. As a result, infected seedlings may not display symptoms until moved to a warm environment.
                    
Treatment :
1)Inspect transplants prior to purchase. Choose only transplants showing no clear symptoms.
2)Avoid planting in fields where tomato root debris is present, as the virus can survive long-term in roots.
3)Wash hands with soap and water before and during the handling of plants to reduce potential spread between plants.
4)Use certified disease-free seed or treat your own seed.
 Soak seeds in a 10% solution of trisodium phosphate (Na3PO4) for at least 15 minutes.
Or heat dry seeds to 158 °F and hold them at that temperature for two to four days.
5)Purchase transplants only from reputable sources. Ask about the sanitation procedures they use to prevent disease.
""",

        'Tomato___healthy':"No information needed , it is healty ",

    }
    return switcher.get(class_name)








