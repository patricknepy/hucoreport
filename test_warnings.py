import sqlite3

conn = sqlite3.connect('data/cache.db')
cursor = conn.cursor()

# Compter les warnings avec LIKE '%warning%'
cursor.execute("""
    SELECT COUNT(*) 
    FROM projects 
    WHERE status = 'EN COURS' 
    AND LOWER(vision_internal) LIKE '%warning%'
""")
count_like = cursor.fetchone()[0]
print(f"🔍 Warnings vision_internal (avec LIKE '%warning%'): {count_like}")

# Compter les warnings avec = 'WARNING !'
cursor.execute("""
    SELECT COUNT(*) 
    FROM projects 
    WHERE status = 'EN COURS' 
    AND UPPER(vision_internal) = 'WARNING !'
""")
count_exact = cursor.fetchone()[0]
print(f"🔍 Warnings vision_internal (exact 'WARNING !'): {count_exact}")

# Lister toutes les valeurs distinctes de vision_internal pour projets actifs
cursor.execute("""
    SELECT DISTINCT vision_internal 
    FROM projects 
    WHERE status = 'EN COURS' 
    AND vision_internal IS NOT NULL
    ORDER BY vision_internal
""")
values = cursor.fetchall()
print(f"\n📋 Valeurs distinctes de vision_internal (projets actifs):")
for val in values:
    print(f"  - [{val[0]}]")

# Lister les projets avec WARNING dans vision_internal
cursor.execute("""
    SELECT id_projet, client_name, vision_internal 
    FROM projects 
    WHERE status = 'EN COURS' 
    AND vision_internal IS NOT NULL
    AND (LOWER(vision_internal) LIKE '%warning%' OR UPPER(vision_internal) LIKE '%WARNING%')
    ORDER BY id_projet
""")
warnings = cursor.fetchall()
print(f"\n⚠️ Liste des projets avec WARNING dans vision_internal:")
for w in warnings:
    print(f"  - Projet #{w[0]} ({w[1]}): [{w[2]}]")

# Comparer avec vision_client
cursor.execute("""
    SELECT COUNT(*) 
    FROM projects 
    WHERE status = 'EN COURS' 
    AND LOWER(vision_client) LIKE '%warning%'
""")
count_client = cursor.fetchone()[0]
print(f"\n🔍 Pour comparaison - Warnings vision_client: {count_client}")

conn.close()


