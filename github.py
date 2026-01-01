import json, os, re

# TÜRKÇE SÖZLÜK
TR_MAP = {
    "N": "İsim", "PN": "Özel İsim", "PRON": "Zamir", "V": "Fiil", 
    "ADJ": "Sıfat", "IMPV": "Emir", "PERF": "Mazi", "IMPF": "Muzari",
    "CONJ": "Bağlaç", "P": "Edat", "DET": "Belirlilik Takısı (ال)",
    "PREF": "Ön Ek", "SUFF": "Son Ek", 
    "ACT_PCPL": "İsm-i Fail", "PASS_PCPL": "İsm-i Meful", "PASS": "Edilgen Yapı (Meçhul)",
    "3MS": "3. Şahıs Eril Tekil (O)", "3FS": "3. Şahıs Dişil Tekil (O)",
    "3MP": "3. Şahıs Eril Çoğul (Onlar)", "3FP": "3. Şahıs Dişil Çoğul (Onlar)",
    "3MD": "3. Şahıs Eril İkil (O İkisi)", "2MP": "2. Şahıs Eril Çoğul (Siz)",
    "2MS": "2. Şahıs Eril Tekil (Sen)", "1P": "1. Şahıs Çoğul (Biz)",
    "M": "Eril", "F": "Dişil", "S": "Tekil", "P": "Çoğul", "D": "İkil",
    "ACC": "Mansub (Üstün/Nesne)", "GEN": "Mecrur (Esre/Tamlayan)", 
    "NOM": "Merfu (Ötre/Özne)", "INDEF": "Belirsiz (Nekre)", "DEF": "Belirli (Marife)",
    "NEG": "Olumsuzluk", "VOC": "Nida (Seslenme)", "REL": "İlgi Zamiri"
}

def generate_data(file_path):
    if not os.path.exists(file_path):
        print(f"Hata: {file_path} bulunamadı!")
        return None, None

    root_map = {}
    verse_map = {} # Ayetleri birleştirmek için (Örn: "1:1" -> "Bismillah...")

    print("Veriler işleniyor, lütfen bekleyin...")

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            parts = line.split('\t')
            if len(parts) < 4: continue
            
            # Konum Parçalama (Örn: 1:1:1:1 -> Sure:Ayet:Kelime)
            loc_parts = parts[0].split(':')
            chapter_verse = f"{loc_parts[0]}:{loc_parts[1]}" # 1:1 (Sure:Ayet)
            
            arabic_text = parts[1]
            pos_tag = parts[2]
            features = parts[3].split('|')

            # 1. AYET İNŞASI (Kelimeleri birleştir)
            if chapter_verse not in verse_map:
                verse_map[chapter_verse] = []
            verse_map[chapter_verse].append(arabic_text)

            # 2. KÖK ANALİZİ
            root = next((f.split(':')[1] for f in features if f.startswith('ROOT:')), None)
            if not root: continue
            
            if root not in root_map: root_map[root] = []
            
            tr_tags = [TR_MAP.get(f, f) for f in features if ":" not in f]
            lemma = next((f.split(':')[1] for f in features if f.startswith('LEM:')), "-")
            
            # Kelime konumunu kaydet (Sure:Ayet:KelimeNo)
            word_loc = ":".join(loc_parts[:3]) 

            root_map[root].append({
                "loc": word_loc,
                "cv": chapter_verse, # Ayeti bulmak için anahtar
                "t": arabic_text, 
                "type": TR_MAP.get(pos_tag, pos_tag),
                "tags": tr_tags, 
                "lem": lemma
            })

    # Listeleri birleştirip cümle yap
    final_verses = {k: " ".join(v) for k, v in verse_map.items()}

    return root_map, final_verses

# ÇALIŞTIRMA
roots, verses = generate_data("quran-morphology.txt")

if roots and verses:
    # 1. Kök Dosyası
    with open("roots_master.json", "w", encoding="utf-8") as f:
        json.dump(roots, f, ensure_ascii=False, indent=2)
    
    # 2. YENİ: Ayet Dosyası
    with open("verses_map.json", "w", encoding="utf-8") as f:
        json.dump(verses, f, ensure_ascii=False, indent=2)
        
    print(f"Başarılı! {len(roots)} kök ve {len(verses)} ayet oluşturuldu.")