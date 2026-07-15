sample_products = [
    {"name": "Yun Şərf", "description": "Qışda isti saxlayan yumşaq yun şərf, boğazı sərinlikdən qoruyur", "price": 25.0, "category": "geyim", "stock": 40},
    {"name": "Yağış Kürkü", "description": "Su keçirməyən, yağışlı havalarda geyilə bilən yüngül kürk", "price": 60.0, "category": "geyim", "stock": 15},
    {"name": "Yay Sandaletləri", "description": "İsti hava üçün rahat, yüngül yay ayaqqabısı", "price": 30.0, "category": "ayaqqabı", "stock": 25},
    {"name": "Termos Stəkan", "description": "İçkini uzun müddət isti saxlayan termo stəkan, qış səfərləri üçün ideal", "price": 18.0, "category": "aksesuar", "stock": 50},
    # ... daha 15-25 məhsul əlavə et (fərqli kateqoriyalar: elektronika, ev əşyaları, idman)
    # Geyim
    {"name": "Pambıq Tişört",
     "description": "Yay aylarında sərinlik verən yüngül pambıq parçadan tişört, gündəlik geyim üçün ideal",
     "price": 15.0, "category": "geyim", "stock": 60},
    {"name": "Dəri Gödəkçə", "description": "Payız və qış üçün stilli, küləkdən qoruyan dəri gödəkçə", "price": 120.0,
     "category": "geyim", "stock": 10},
    {"name": "İstirahət Pijaması", "description": "Evdə rahat istirahət üçün yumşaq, nəfəs alan parçadan pijama dəsti",
     "price": 22.0, "category": "geyim", "stock": 35},
    {"name": "İdman Tayt", "description": "Qaçış və fitness zamanı rahatlıq verən elastik idman taytı", "price": 28.0,
     "category": "geyim", "stock": 45},
    {"name": "Uşaq Qış Kombinezonu",
     "description": "Kiçik uşaqları soyuqdan qoruyan isti, su keçirməyən qış kombinezonu", "price": 45.0,
     "category": "geyim", "stock": 20},

    # Ayaqqabı
    {"name": "Qış Botları", "description": "Qarlı və soyuq havada ayaqları isti saxlayan su keçirməyən bot",
     "price": 75.0, "category": "ayaqqabı", "stock": 18},
    {"name": "Qaçış Ayaqqabısı",
     "description": "Yüngül, yumşaq döşəməli, uzun məsafəli qaçış üçün nəzərdə tutulmuş idman ayaqqabısı",
     "price": 55.0, "category": "ayaqqabı", "stock": 30},
    {"name": "Rəsmi Dəri Ayaqqabı", "description": "İş görüşləri və rəsmi tədbirlər üçün zərif dəri ayaqqabı",
     "price": 65.0, "category": "ayaqqabı", "stock": 12},

    # Aksesuar
    {"name": "Yun Əlcəklər", "description": "Soyuq qış günlərində əlləri isti saxlayan yumşaq yun əlcək", "price": 12.0,
     "category": "aksesuar", "stock": 50},
    {"name": "Günəş Eynəyi", "description": "Yay günəşindən qorunmaq üçün UV filtrli stilli eynək", "price": 20.0,
     "category": "aksesuar", "stock": 40},
    {"name": "Dəri Kəmər", "description": "Klassik dəri kəmər, həm gündəlik, həm rəsmi geyimlərə uyğun", "price": 18.0,
     "category": "aksesuar", "stock": 25},
    {"name": "Papaq (Qış)", "description": "Başı və qulaqları soyuqdan qoruyan isti yun papaq", "price": 14.0,
     "category": "aksesuar", "stock": 38},

    # Elektronika
    {"name": "Simsiz Qulaqlıq", "description": "Səyahət və idman zamanı musiqi dinləmək üçün rahat simsiz qulaqlıq",
     "price": 40.0, "category": "elektronika", "stock": 22},
    {"name": "Portativ Powerbank",
     "description": "Telefon və planşetləri yolda şarj etmək üçün yüksək tutumlu portativ enerji bankı", "price": 35.0,
     "category": "elektronika", "stock": 28},
    {"name": "Ağıllı Saat", "description": "Nəbz, addım və yuxu izləyən, bildirişləri göstərən ağıllı saat",
     "price": 90.0, "category": "elektronika", "stock": 15},

    # Ev əşyaları
    {"name": "Elektrik Adyal", "description": "Qış gecələrində yatağı isti saxlayan tənzimlənə bilən elektrik adyalı",
     "price": 50.0, "category": "ev əşyaları", "stock": 16},
    {"name": "Aromaterapiya Şam Dəsti", "description": "Evdə rahatlıq və isti atmosfer yaradan ətirli şam dəsti",
     "price": 20.0, "category": "ev əşyaları", "stock": 33},
    {"name": "Yumşaq Pled", "description": "Divanda soyuq axşamlarda isinmək üçün yumşaq, isti saxlayan pled",
     "price": 28.0, "category": "ev əşyaları", "stock": 24},

    # İdman
    {"name": "Yoga Xalçası", "description": "Yoga və gərginlik açma məşqləri üçün rahat, sürüşməyən xalça",
     "price": 25.0, "category": "idman", "stock": 27},
    {"name": "Fitness Su Butulkası",
     "description": "İdman zalında və açıq havada istifadə üçün yüngül, sızdırmayan su qabı", "price": 10.0,
     "category": "idman", "stock": 55},

# İçki/Qida
    {"name": "İsti Şokolad Qarışığı", "description": "Soyuq qış axşamlarında isinmək üçün krem-şokolad dadlı isti içki tozu", "price": 8.0, "category": "içki", "stock": 40},
    {"name": "Bitki Çayı Dəsti", "description": "Rahatlaşdırıcı, isti içilən nanə-məlisə qarışıqlı bitki çayı toplusu", "price": 12.0, "category": "içki", "stock": 35},
    {"name": "Enerji İçkisi", "description": "İdman və fəal gün üçün canlandırıcı, soyuq içilən enerji içkisi", "price": 5.0, "category": "içki", "stock": 60},
    {"name": "Termos Qəhvə Fincanı", "description": "Səyahətdə qəhvəni uzun müddət isti saxlayan izolyasiyalı fincan", "price": 15.0, "category": "içki", "stock": 25},
]