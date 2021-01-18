import csv
import datetime
import random
from io import StringIO

import requests

from data.models import *

english = """
because i am super duber dumb ;-;,-0.957505494
because I love shawarma house and its quality plus reasonable price,0.975
Because i love this brand,0.975
Because it is great,0.975
Because it taste good,0.975
Because its good,0.975
Because the service is nice,0.975
because they delever fast,0.975
because they give quick delivery,0.975
Bjjj,0
Cause I know about that restaurant and I like it,0.975
chjbv ggv g g  f gg f,0
"Couldnt order, it kept telling me payment not processing",-0.975
Customer service,0
delicious taste,0.975
delivereied fast and with good taste,0.975
Delivery on time,0.975
Delivery on time with fresh best quality of food,0.975
"delivery speed , fresh food",0.975
delivery time,0
Dhbb,0
Dhbb,0
easy,0.975
Easy and reliable and cheap,0.975
easy convenient,0.975
Easy for use,0.975
Easy to use,0.975
Easy to use and easy to order,0.975
Excellent service,0.975
Fast and tasty,0.975
Fast delivery,0.975
Fast-connecting,0.975
fdfdfdf,0
Ffdse,0
fuck off,-0.975
good,0.975
Good,0.975
Good,0.975
Good,0.975
good,0.975
Good,0.975
good  quality,0.975
good [prices,0.975
Good app,0.975
Good experience,-0.975
good quality,0.975
Good quality of food and good service,0.975
Good Quality-Fast Delivery-not bad prices,0
good service,0.975
Great taste,0.975
Gud app,0
Hhhh,0
home orders,0
home orders,0
HungerStation The Chefz Careem Now Lugmety Mrsool Jahez Talabat Wssel Walem ToYou Shgardi TmmT,0
i  like it,0
i do kinda like it,0.975
i like  shawarma,0.975
i like eating to restourent,0.975
I like it,0.975
I like it,0.975
I like taste,0.975
I like the appto order usually ill go to dine out,0
I like this app,0.975
I love it,0.975
I love the app,0.975
I love the taste and price are affordable,0.975
I need my credit,0
I received my order,0
It has high quality and it's easy to use,0.975
It has the best shawarma,0.975
It is good,0.975
It is good,0.975
It is good,0.975
it tasted very good i liked and all my family liked it,0.975
It tastes very good,0.975
it was tasty,0.975
It's easy and have a lot of offers,0.975
Its easy to get food rather than going outside because of the pandemic.,0.019786243
It's good in menu and payment type,0.946976928
It's good. Fast delivery nice deliverers .,0.975
"It's not bad,, also not up to the standard",0.966963268
Its quick and fast,0.975
its really tasty and trust worthy,0.975
Its user friendly app and quick in action,0.975
Just for surveys,0
kjh,0
messy,-0.975
more expencve,0
Msiz,0
nice pictures,0.975
Price,0
"Quick service, saving time",0.975
really like shawarma,0.975
Services is verygood,0
sfdsfds dsfdsfdsfd sfdsfds fdsf dsf dsfdsfd,0
sharwma,0
shawarmashse,0
showermer,0
sj,0
Teast is awesome,0.975
The app was easy to use,0.966963268
the delivery was quick,0.975
The quality of food is good. The service and delivery is great.,0.975
the sharwarma was very good and the price abordable,0.975
the staff and order is fast,0.966963268
The taste is different to others,0.966963268
There was offer only on pick up not delivery,0
They deliver fast,0.975
they serve well,0.975
they served fresh,0.975
TIME SAVING AND HOME DELIVERY,0.975
To good,0.975
user friendly,0.975
vcfde,0
Very good testy,0.975
Very tasty and easy app,0.975
Very tasty and healthy,0.975
"We know this is a great delivery application,",0.935427514
Xyixi,0
Yummy food,0.975
"""

arabic = """
الاكل التظافة,-0.975
الطعم,-0.975
الطعم,-0.975
الطعم والسرعة,-0.975
اموت عليه,-0.975
انه ياخذ وقت اطول,-0.975
بتموصبوتى,-0.975
تأخير الطلب,-0.975
جربته الأسبوع الماضي وعند تنفيذ الطلب لم يتم التنفيذ ويقولي رسالة انتهى العرض بالرغم من الإعلان عن توفره,-0.975
عادى,-0.975
عادي,-0.975
عادي,-0.975
عادي مثل باقي المطاعم,-0.975
لا يوجد,-0.975
لا يوجد,-0.975
لانه يلبى الغرض,-0.975
م يحتاج تقييم لانو يهبل,-0.975
مشكلة تعليق تطبيق,-0.975
كان هناك عرض على التطبيق لمدة يومين وعند تنفيذ الطلب لم يكتمل بحجة انتهاء العرض وهذا عدم التزام بموعد هم من حددوه,-0.9108138275441720
الطقعن,-0.422
السعر,0
الشاومر مليى بالزين,0
الطعم وجوده الاكل,0
النوصيل,0
انا ابي مقابل حيوان نادر,0
بعيد عني,0
ةاربر,0
ةةغا٥,0
تمت التجربة,0
جدا,0
جيدا الدجاج,0.975
دايم اشتري منه,0
سننس,0
صثقفغ,0
ع,0
عشان تغير للاسوء,0
عندما كان قالت ليك أن أكون لاعب في كل مكان أخضر,0
فففففهههههها,0
كثرة الطلب,0
ل,0
لا اعلم,0
لا يعجبني بطيئ,-0.975
لاا  رترتتتر,0
لااعلم,0
لاشيء,0
لانه بطيئ جدا,0
لانه تستحق المنافسة,0
لانه لذيذ جداً ورخيص,0.975
لانهم سريعون في تجهيز الطلب,0.975
لانى جربت الاكل فيه طعم لذيذ,0.975
لايوجد,0
لذيذ ورخيص,0.975
لسرعه التوصيل وحراره الاكل,0.975
لعع,0
لنه راءع السؤال,0
مامانورہ,0
مجرب,0
مختلف,0
مستفز,0
مطعم رائع ولكن التسليم بطيء,0
ممتاز ولكن اسعاره غالية,0
نسنسنسىسىستستشتششت,0
هارون,0
هذا ما أشعر به حقاً,0
هنقرستيشن,0
وجود انواع مختلفة,0
يشصبشب,0
التوصيل سريع ولكن لاستجابة بطيئة,0.42493432778761100
بسبب أنه جيد ولذيذ لكن غالي الثمن,0.42493432778761100
بسبب أنه جيد ولذيذ لكن غالي الثمن,0.42493432778761100
لانه نظيف واكله لذيذ,0.42493432778761100
لاني تجربه الاكل نوعا ما جيدة,0.42493432778761100
لذيذ و رخيص و سريع,0.42493432778761100
ممتاز وخفيف التصفح وسريع التوصيل,0.42493432778761100
اكله نظيف وطعمه رائع,0.5611798493101560
انه تطبيق سهل الاستخدام والاكل يصل سريعا وطازجا,0.5611798493101560
أولا لأن الاكل لذيذ والنصوص لذيييذ جداً 😍😍,0.5611798493101560
توصيل سريع دفع أمن مضمون الاكل يوصل ساخن ولذيذ,0.7733656641952620
اما اصلا احب العلامة التجارية هذه بالاضافة الخدمة التوصيل في الوقت المحدد,0.8952002596247640
لانه مطعم جدا جميل وانت طلبت من التقييم,0.9469769280244470
لاني جربته اكثر من ١٠ مرات وعجبني,0.9575054935196870
مطعم ذو نظافة عالية وسرعة فى الطلبات,0.9575054935196870
سرعة التوصيل، سهولة استخدام التطبيق، خدمة العملاء جيدة,0.9599100210564470
قدم عرض ولم يطبقه والغى الطلب,0.9669632681220450
احبة الشاورما,0.975
احبه,0.975
احبه جدا,0.975
احبه جدا,0.975
احبه سهل وسريع,0.975
احلي مطعم شاورما وعروض ممتازه,0.975
احلي مطعم شاورما وعروض ممتازه,0.975
احلي مطعم شاورما وعروض ممتازه,0.975
احلي مطعم شاورما وعروض ممتازه,0.975
اسعار التطبيق معقوله وايضا الوقت الي الوصول جيد جدا,0.975
اسهل واسرع تطبيق للشاورما,0.975
اعجبنى الطعام,0.975
افضل شاورما هي شاورمر,0.975
افضله,0.975
اكلهم رائع و تطبيقهم سهل الاستخدام,0.975
الانه لذيذ جدا,0.975
الانهيار جيد جدا,0.975
التوصيل سريع,0.975
التوصيل سريع,0.975
التوصيل فى الميعاد المحدد,0.975
الجودة,0.975
الجودة,0.975
الجودة العالية,0.975
الجودة والطعم الممتاز بالإضافة إلى التعامل الراقي جدا,0.975
الجوده والسعر,0.975
الجوده والطعم وتوصيل,0.975
السرعة,0.975
السرعة في التوصيل,0.975
السرعه والسهولة,0.975
الشاورما روعه وطعمها طيب وتتبيلتها مميزة,0.975
الطعام جودته عاليه ومذاق ممتاز,0.975
الطعام طازج,0.975
الطعم الجيد,0.975
الطعم الفريد,0.975
الطعم رائع والعروض اروع,0.975
الطعم لذيذ,0.975
الطعم والتوصيل سريع,0.975
المنتج جودته ممتازة,0.975
النظافة الجودة,0.975
انني احب مطاعم ااشاورما,0.975
انني جربته واعجبني جداً,0.975
انني جربته واعجبني جداً,0.975
انه جيد,0.975
انه رائع ومميز جدا,0.975
انه لذيذ,0.975
انه ممتاز,0.975
انها مسأله شخصيه,0.975
اني احبهم جدا,0.975
بسبب طيبة الشاورما,0.975
تجربة ايجابية جيده,0.975
تطبيق اعجبني,0.975
تطبيق جميل واسرع,0.975
تطبيق جيد,0.975
تطبيق سهل الاستخدام,0.975
تطبيق سهل وسريع,0.975
تطبيق ممتاز واحب الشاورما الخاصه به,0.975
تطبيق ممتاز يخدم شاورما فقط,0.975
توصيل ع الوقت,0.975
جدا ممتاز,0.975
جدير بالثقة,0.975
جربته خدمه رائعه وطعم جيد,0.975
جربته ولذيذ ونضيف,0.975
جميل,0.975
جميل,0.975
جميل,0.975
جميل,0.975
جميل جدا,0.975
جميل جدا جدا,0.975
جميل جدا والله,0.975
جميل روعه,0.975
جمييييل,0.975
جودة الخدمة,0.975
جودة المنتج,0.975
جودته عاليه,0.975
جوده الطعم وسرعه التوصيل,0.975
جوده طعم الشاورما لذيذه,0.975
جوده عاليه,0.975
جيد,0.975
جيد,0.975
جيد,0.975
جيد,0.975
جيد,0.975
جيد,0.975
جيد,0.975
جيد,0.975
جيد,0.975
جيد,0.975
جيد,0.975
جيد,0.975
جيد,0.975
جيد,0.975
جيد التوصيل,0.975
جيد جدا,0.975
جيد نوعا ما,0.975
جيد والطعام لذيذ,0.975
جيده,0.975
خدمة سريعة,0.975
خدمة ممتاز,0.975
خدمة ممتازة وجودة عالية,0.975
خدمه سريعه وجيدة,0.975
خدمه ممتازه,0.975
خمة جيدة وينقصها دقة المواعيد,0.975
رائع المذاق,0.975
رائع جدا,0.975
رائع جدا,0.975
رخيص وسريع,0.975
سرعة التوصيل,0.975
سرعة التوصيل,0.975
سرعة لذيذ مريح,0.975
سرعة والاكل طازج,0.975
سرعه التوصيل وجوزه المنتج,0.975
سريع,0.975
سريع,0.975
سريع,0.975
سريع ولذيذ,0.975
سلس وسريع,0.975
سنويتش الشاورما عندهم كبير وسعره حلو  والتطبيق سهل الاستخدام,0.975
سهل,0.975
سهل,0.975
سهل الاستخدام,0.975
سهل الاستخدام ومتنوع,0.975
سهل التوصيل,0.975
سهل وبسيط,0.975
سهل وسريع,0.975
سهولته,0.975
شاورما جيده جدا,0.975
شاورما لذيذة جدا,0.975
شاورما لذيذه,0.975
شاورما مميزه,0.975
شورمر جودة في الاداء,0.975
طازج,0.975
طعم جميل,0.975
طعم جيد وجبه مشبعه,0.975
طعم جيد وسرعه وجودة,0.975
طعم رائع,0.975
طعم لا يقاوم,0.975
طعمه جداا,0.975
طعمه جداا,0.975
طعمه جداا,0.975
طعمه جداا,0.975
طعمه جميل,0.975
طعمه شهي جدا,0.975
طعمه لذيذ,0.975
طعمه لذيذ جدا,0.975
طعمه مميز مع ان السعر مرتفع ولاكن يستحق,0.975
طلبتها اعجبت افراد الاسره,0.975
طناخه,0.975
عصري ومتجدد,0.975
فريد في المذاق,0.975
كل شى كان جيد,0.975
لان المذاق رائع وسريعين في التوصيل,0.975
لان النطبيق جيد جدا,0.975
لان طعمه لذيذ,0.975
لانك سألتني و لازم اجاوب,0.975
لانني احبه,0.975
لانه جذبني,0.975
لانه جميل,0.975
لانه سريع,0.975
لانه لذيذ وجميل,0.975
لانه لذيذ وجودته عاليه,0.975
لانه مطعم رائع وذو مذاقٍ لذيذذ,0.975
لانه مطعم ناجح وطعم الشاورما لذيذ,0.975
لانه ممتاز,0.975
لانه مميز,0.975
لانه يستحق,0.975
لانه يستحق,0.975
لانه يوجد الافضل منه,0.975
لانها لذيذه,0.975
لاني احبه,0.975
لاني احبه,0.975
لاني احبه جدا,0.975
لاني احبه مره,0.975
لاني فقط احب الشاورما,0.975
لأن الخبز طريّ واللحم لذيذ والصوص لذيذ جداً,0.975
لأنه دائما طازج وطعمه لذيذ,0.975
لأنه لذيذ,0.975
لأنه مطعمي المفضل,0.975
لأنها جيدا,0.975
لأنها ممتازا,0.975
لأنهم يوصلون الطلبات سريعاً,0.975
لديه شاورما بطعم رائع وطازج  وباسعار رائعه,0.975
لذيذ,0.975
لذيذ,0.975
لذيذ,0.975
لذيذ,0.975
لذيذ,0.975
لذيذ الطعم وسعر مناسب,0.975
لذيذ وجيد,0.975
لذيذة,0.975
لذيذه جداً,0.975
متكامل,0.975
متميز وذو جوده,0.975
مذاقه لذيذ,0.975
مذاقه لذيذ,0.975
مذاقه لذيذ,0.975
مرههههههههههههه  لذيذ,0.975
مستوى الجودة,0.975
مطعم ذا جودة عالية,0.975
مطعم رائع,0.975
مطعم شاورمر معروف بالمذاق الجميل,0.975
مطعم متميز,0.975
مطعم مميز,0.975
مطعم من الدرجه الاولي من حيث النظافة والطعم اللذيذ,0.975
مطعم موثوق واحب طعم شاورمته,0.975
مطعم نضيف ويستاهل,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز,0.975
ممتاز فى كل شى,0.975
ممتاز و سريع التوصيل,0.975
مميز,0.975
مميز,0.975
مميز,0.975
مميز,0.975
مميز,0.975
مميز,0.975
مميز,0.975
مميز جدا,0.975
من عاشقي الشاورما 😍😍,0.975
نظيف وممتاز,0.975
يستحق,0.975
يعجبني,0.975
يعجبني,0.975
يعجبني,0.975
"""

data = [
    ('en', english),
    ('ar', arabic),
]

def run():
    proj, _ = Project.objects.get_or_create(name='Muhimma Demo')
                
    country, _ = Country.objects.get_or_create(label='Saudi Arabia')
    source, _ = Source.objects.get_or_create(label='Muhimma Survey')

    for lang, csv_data in data:
        
        f = StringIO(csv_data)
        reader = csv.reader(f)
        
        for row in reader:
            if row:
                text, sentiment = row
                
                keywords = requests.post('https://api.repustate.com/v4/repustatedemopage/keywords.json', 
                        {'text':text, 'lang':lang}).json()
                
                d = Data.objects.create(
                    date_created=datetime.date(2021, 1, 8) + datetime.timedelta(random.randint(0, 10)),
                    project=proj, 
                    country=country,
                    source=source,
                    text=text, 
                    language=lang,
                    sentiment=sentiment, 
                    weighted_score=sentiment,
                )

                for kw in keywords['keywords']:
                    if kw.strip():
                        k, _ = Keyword.objects.get_or_create(label=kw)
                        d.keywords.add(k)
