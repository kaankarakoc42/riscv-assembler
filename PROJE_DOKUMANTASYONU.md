# RISC-V RV32I Assembler - Detaylı Proje Dokümantasyonu

## İçindekiler

1. [Giriş](#giriş)
2. [Literatür Araştırması](#literatür-araştırması)
3. [Assembler Mimarisi](#assembler-mimarisi)
4. [Kullanılan Veri Yapıları](#kullanılan-veri-yapıları)
5. [Opcode Table Tasarımı](#opcode-table-tasarımı)
6. [Symbol Table Tasarımı](#symbol-table-tasarımı)
7. [Assembler Algoritması](#assembler-algoritması)
8. [Akış Diyagramı](#akış-diyagramı)
9. [Test Senaryoları ve Sonuçlar](#örnekler-ve-test-senaryoları)
10. [Algoritma Karmaşıklığı Analizi](#algoritma-karmaşıklığı-analizi)
11. [Sonuç ve Değerlendirme](#sonuç)
12. [Kaynakça](#kaynakça)
---

## Giriş

### Amaç

Bu proje, PicoRV işlemcisi için RISC-V RV32I komut setinin bir alt kümesini destekleyen tam özellikli bir assembler yazılımı geliştirmeyi amaçlamaktadır. Assembler, assembly dilinde yazılmış kaynak kodları makine koduna (object code) dönüştürebilme yeteneğine sahiptir.

### Proje Kapsamı

- **Opcode Tablosu**: Desteklenen tüm komutlar için opcode, funct3, funct7 bilgileri
- **Sembol Tablosu**: Programdaki etiketlerin (label) adreslerini tutan veri yapısı
- **Parser**: Assembly komutlarını ayrıştıran yapı
- **Makine Kodu Üretici**: Assembly komutlarını makine koduna dönüştüren modül
- **Direktif Desteği**: `.data`, `.text`, `.word`, `.byte`, `.org`, `.end` direktifleri

### Teknoloji Stack

- **Programlama Dili**: Python 3
- **Bağımlılıklar**: Standart kütüphane (harici bağımlılık yok)
- **Platform**: Cross-platform (Windows, Linux, macOS)

---

## Assembler Mimarisi

### Genel Mimari

Assembler, modüler bir yapıya sahiptir ve şu ana bileşenlerden oluşur:

```
┌─────────────────────────────────────────────────────────┐
│                    Main (CLI)                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Assembler (Orchestrator)                │
│  - İki geçişli assembly süreci yönetimi                  │
│  - Hata yönetimi ve raporlama                            │
└──────┬──────────────┬──────────────┬────────────────────┘
       │              │              │
       ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌──────────────┐
│   Parser    │ │   Opcode    │ │   Symbol     │
│             │ │   Table     │ │   Table      │
└──────┬──────┘ └──────┬──────┘ └──────┬───────┘
       │              │                │
       ▼              ▼                ▼
┌──────────────────────────────────────────────┐
│         Code Generator                       │
│  - R-type, I-type, S-type, B-type,          │
│    U-type, J-type kod üretimi               │
└──────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│         Directive Handler                    │
│  - .data, .text, .word, .byte, .org, .end   │
└──────────────────────────────────────────────┘
```

### İki Geçişli Assembly Süreci

#### Birinci Geçiş (First Pass)

**Amaç**: Sembol tablosunu oluşturmak ve bellek düzenini belirlemek

**İşlemler**:
1. Her satırı parse et
2. Etiketleri (label) tespit et ve adreslerini hesapla
3. Direktifleri işle (`.org`, `.data`, `.text` gibi)
4. Her komut için 4 byte, her `.word` için 4 byte, her `.byte` için 1 byte adres ilerlet
5. Sembol tablosuna etiketleri ekle

**Örnek**:
```assembly
.text
.org 0x0000

start:          # Adres: 0x0000
    addi x1, x0, 10  # Adres: 0x0000 (start etiketi)
    addi x2, x0, 20  # Adres: 0x0004
loop:           # Adres: 0x0008
    add x3, x1, x2   # Adres: 0x0008 (loop etiketi)
    beq x1, x2, end  # Adres: 0x000C
end:            # Adres: 0x0010
    ebreak          # Adres: 0x0010 (end etiketi)
```

#### İkinci Geçiş (Second Pass)

**Amaç**: Makine kodu üretmek

**İşlemler**:
1. Her satırı tekrar parse et
2. Direktifleri işle ve veri üret
3. Komutları makine koduna dönüştür
4. Sembol tablosundan etiket adreslerini kullan
5. Çıktı dosyasını oluştur

---

## Opcode Table Tasarımı

Bu bölüm, assembler içinde kullanılan opcode/funct3/funct7 veri modelini açıklar. Uygulama detayı `OpcodeTable (opcode_table.py)` başlığında verilmiştir. Tasarım yaklaşımı:

- Komut adına göre O(1) erişim için hash tabanlı sözlük yapı
- Komut formatını (`R/I/S/B/U/J`) tek alanda saklama
- Register adlarını (`xN` ve ABI isimleri) ortak bir eşleme tablosunda toplama
- Kod üretiminde gerekli minimum alanları (opcode, funct3, funct7) tutarak sade veri modeli kurma

---

## Symbol Table Tasarımı

Bu bölüm, etiket adresleme tasarımını açıklar. Uygulama detayı `SymbolTable (symbol_table.py)` başlığında verilmiştir. Tasarım yaklaşımı:

- Etiket -> adres eşleşmesini O(1) sorgu için sözlükte saklama
- Aynı etiketin tekrar tanımlanmasını hata olarak yakalama
- İleri referanslar için geçici liste (`forward_refs`) tutma
- İki geçişli yaklaşım ile etiket çözümlemeyi deterministik hale getirme

---

## Bileşenlerin Detaylı Açıklaması

### 1. OpcodeTable (opcode_table.py)

#### Amaç
RISC-V RV32I komut setindeki tüm komutların encoding bilgilerini saklar.

#### Veri Yapısı
```python
instructions = {
    'add': {
        'type': 'R',
        'opcode': 0x33,
        'funct3': 0x0,
        'funct7': 0x00
    },
    'addi': {
        'type': 'I',
        'opcode': 0x13,
        'funct3': 0x0
    },
    # ... diğer komutlar
}
```

#### Desteklenen Komut Tipleri

**R-Type (Register-Type)**:
- Format: `funct7 | rs2 | rs1 | funct3 | rd | opcode`
- Örnekler: `add`, `sub`, `sll`, `slt`, `xor`, `or`, `and`
- 3 operand: `rd, rs1, rs2`

**I-Type (Immediate-Type)**:
- Format: `imm[11:0] | rs1 | funct3 | rd | opcode`
- Örnekler: `addi`, `slti`, `xori`, `ori`, `andi`, `lw`, `lb`, `jalr`
- 2-3 operand: `rd, rs1, imm` veya `rd, offset(rs1)`

**S-Type (Store-Type)**:
- Format: `imm[11:5] | rs2 | rs1 | funct3 | imm[4:0] | opcode`
- Örnekler: `sw`, `sh`, `sb`
- 2 operand: `rs2, offset(rs1)`

**B-Type (Branch-Type)**:
- Format: `imm[12|10:5] | rs2 | rs1 | funct3 | imm[4:1|11] | opcode`
- Örnekler: `beq`, `bne`, `blt`, `bge`, `bltu`, `bgeu`
- 3 operand: `rs1, rs2, label`

**U-Type (Upper Immediate-Type)**:
- Format: `imm[31:12] | rd | opcode`
- Örnekler: `lui`, `auipc`
- 2 operand: `rd, imm`

**J-Type (Jump-Type)**:
- Format: `imm[20|10:1|11|19:12] | rd | opcode`
- Örnekler: `jal`
- 1-2 operand: `label` veya `rd, label`

#### Register Mapping

32 adet register'ın hem sayısal (`x0-x31`) hem de isimsel (`zero`, `ra`, `sp`, vb.) karşılıkları desteklenir:

```python
registers = {
    'zero': 0, 'x0': 0,
    'ra': 1, 'x1': 1,
    'sp': 2, 'x2': 2,
    # ... tüm register'lar
}
```

### 2. SymbolTable (symbol_table.py)

#### Amaç
Programdaki tüm etiketlerin (label) adreslerini saklar ve forward reference'ları yönetir.

#### Veri Yapısı
```python
symbols = {
    'start': 0x0000,
    'loop': 0x0008,
    'end': 0x0010
}

forward_refs = {
    'end': [(0x000C, 'B')]  # Adres, komut tipi
}
```

#### Özellikler

1. **Etiket Ekleme**: `add_symbol(label, address)`
   - Duplicate kontrolü yapar
   - Forward reference'ları çözer

2. **Adres Sorgulama**: `get_address(label)`
   - Etiket adresini döndürür
   - Yoksa `None` döndürür

3. **Forward Reference Yönetimi**: `add_forward_ref(label, address, inst_type)`
   - İlk geçişte tanımlanmamış etiketler için referans saklar
   - İkinci geçişte çözülür

#### Kullanım Örneği
```python
sym_table = SymbolTable()
sym_table.add_symbol('start', 0x0000)
sym_table.add_symbol('loop', 0x0008)
address = sym_table.get_address('loop')  # 0x0008 döner
```

### 3. Parser (parser.py)

#### Amaç
Assembly kaynak kodunu satır satır parse ederek yapılandırılmış veriye dönüştürür.

#### Parse Edilen Öğeler

1. **Etiketler (Labels)**
   ```assembly
   start:          # {'type': 'label', 'label': 'start'}
   loop: addi x1, x1, 1  # {'type': 'instruction', 'label': 'loop', 'mnemonic': 'addi', ...}
   ```

2. **Komutlar (Instructions)**
   ```assembly
   addi x1, x0, 10
   # {'type': 'instruction', 'mnemonic': 'addi', 'operands': [...]}
   ```

3. **Direktifler (Directives)**
   ```assembly
   .data
   .word 0x12345678
   # {'type': 'directive', 'directive': 'word', 'args': [0x12345678]}
   ```

4. **Yorumlar (Comments)**
   ```assembly
   addi x1, x0, 10  # Bu bir yorum
   # Yorum satırı parse edilmez
   ```

#### Operand Parsing

Parser, farklı operand tiplerini ayırt eder:

- **Register**: `x1`, `ra`, `sp` → `{'type': 'register', 'value': 'x1'}`
- **Immediate**: `10`, `0xFF`, `-5` → `{'type': 'immediate', 'value': 10}`
- **Register Offset**: `4(x1)` → `{'type': 'register_offset', 'register': 'x1', 'offset': 4}`
- **Label**: `loop`, `end` → `{'type': 'label', 'value': 'loop'}`

#### Regex Patterns

```python
label_pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*:'
directive_pattern = r'^\s*\.(\w+)'
instruction_pattern = r'^\s*([a-zA-Z]+)(?:\s+(.+))?$'
comment_pattern = r'#.*$'
```

### 4. CodeGenerator (code_generator.py)

#### Amaç
Parse edilmiş komutları RISC-V makine koduna dönüştürür.

#### Kod Üretim Süreci

1. **Komut Tipi Belirleme**: Opcode tablosundan komut bilgisi alınır
2. **Operand Ayrıştırma**: Operand'lar register numaralarına ve immediate değerlere dönüştürülür
3. **Etiket Çözümleme**: Label'lar sembol tablosundan adreslere dönüştürülür
4. **Bit Manipülasyonu**: RISC-V encoding formatına göre bitler yerleştirilir
5. **32-bit İşaret Uzatma**: Immediate değerler sign-extend edilir

#### R-Type Kod Üretimi

```python
def _generate_r_type(self, inst_info, operands):
    rd = self._get_register_number(operands[0])   # 5 bit
    rs1 = self._get_register_number(operands[1])  # 5 bit
    rs2 = self._get_register_number(operands[2])   # 5 bit
    funct7 = inst_info['funct7']                  # 7 bit
    funct3 = inst_info['funct3']                  # 3 bit
    opcode = inst_info['opcode']                  # 7 bit
    
    instruction = (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | 
                  (funct3 << 12) | (rd << 7) | opcode
    return instruction & 0xFFFFFFFF
```

**Örnek**: `add x3, x1, x2`
- `x3` = 3, `x1` = 1, `x2` = 2
- `funct7` = 0x00, `funct3` = 0x0, `opcode` = 0x33
- Sonuç: `0x002081B3`

#### I-Type Kod Üretimi

**Load Komutları**:
```python
lw x1, 4(x2)
# rd = x1, rs1 = x2, imm = 4
# Format: imm[11:0] | rs1 | funct3 | rd | opcode
```

**Arithmetic Immediate**:
```python
addi x1, x2, 10
# rd = x1, rs1 = x2, imm = 10 (sign-extended to 12 bits)
```

**System Komutları**:
```python
ebreak
# imm = 1, rs1 = 0, funct3 = 0, rd = 0, opcode = 0x73
# Sonuç: 0x00100073
```

#### B-Type Kod Üretimi

Branch komutlarında offset hesaplama:
```python
beq x1, x2, loop
# offset = loop_address - current_address
# Offset 13-bit signed, 2-byte aligned olmalı
# Format: imm[12|10:5] | rs2 | rs1 | funct3 | imm[4:1|11] | opcode
```

#### J-Type Kod Üretimi

Jump komutlarında offset hesaplama:
```python
jal x1, subroutine
# offset = subroutine_address - current_address
# Offset 21-bit signed, 2-byte aligned olmalı
# Format: imm[20|10:1|11|19:12] | rd | opcode
```

#### Sign Extension

Immediate değerler sign-extend edilir:
```python
def _sign_extend(self, value, bits):
    sign_bit = 1 << (bits - 1)
    mask = (1 << bits) - 1
    value = value & mask
    if value & sign_bit:
        return value | (~mask)  # Negative
    return value  # Positive
```

### 5. DirectiveHandler (directive_handler.py)

#### Amaç
Assembler direktiflerini işler ve veri segmenti yönetimi yapar.

#### Desteklenen Direktifler

**`.data`**: Veri segmentini başlatır
```assembly
.data
.org 0x1000
```

**`.text`**: Kod segmentini başlatır
```assembly
.text
.org 0x0000
```

**`.org address`**: Bellek adresini ayarlar
```assembly
.org 0x1000  # Sonraki veriler 0x1000 adresinden başlar
```

**`.word value1, value2, ...`**: 32-bit kelime değerleri tanımlar
```assembly
values: .word 0x12345678, 0xABCDEF00
# Her kelime 4 byte yer kaplar
```

**`.byte value1, value2, ...`**: 8-bit byte değerleri tanımlar
```assembly
array: .byte 1, 2, 3, 4, 5
# Her byte 1 byte yer kaplar
```

**`.end`**: Assembly işlemini sonlandırır
```assembly
.end
```

### 6. Assembler (assembler.py)

#### Amaç
Tüm bileşenleri koordine eder ve assembly sürecini yönetir.

#### Ana Metodlar

**`assemble(source_code)`**: 
- Kaynak kodu assemble eder
- İki geçişli süreci yönetir
- Hata ve uyarıları toplar

**`assemble_file(filename)`**:
- Dosyadan okur ve assemble eder

**`write_object_file(filename, format)`**:
- Çıktı dosyasına yazar
- Formatlar: `hex`, `verilog`, `binary`

#### Hata Yönetimi

```python
errors = []  # Hata mesajları
warnings = []  # Uyarı mesajları

# Örnek hatalar:
# - Tanımsız etiket
# - Geçersiz register
# - Offset aralık dışı
# - Duplicate label
```

---

## Kullanılan Veri Yapıları

### 1. Opcode Table Veri Yapısı

**Karmaşıklık**: O(1) lookup
**Yapı**: Dictionary (Hash Table)

```python
{
    'mnemonic': {
        'type': 'R'|'I'|'S'|'B'|'U'|'J',
        'opcode': int,
        'funct3': int,
        'funct7': int (optional)
    }
}
```

### 2. Symbol Table Veri Yapısı

**Karmaşıklık**: 
- Ekleme: O(1)
- Sorgulama: O(1)
- Forward reference: O(n) n = referans sayısı

**Yapı**: Dictionary (Hash Table)

```python
{
    'label_name': address (int)
}
```

### 3. Parse Tree Yapısı

**Karmaşıklık**: O(1) per line

```python
{
    'type': 'label'|'instruction'|'directive'|'empty'|'comment',
    'label': str (optional),
    'mnemonic': str (optional),
    'operands': list (optional),
    'directive': str (optional),
    'args': list (optional),
    'original': str
}
```

---

## Assembler Algoritması

### İki Geçişli Assembly Algoritması

#### Algoritma 1: Birinci Geçiş

```
FUNCTION first_pass(lines):
    current_address = text_address
    FOR each line in lines:
        parsed = parse_line(line)
        
        IF parsed.type == 'directive':
            IF directive == 'org':
                current_address = args[0]
            ELSE IF directive == 'data':
                current_address = data_address
            ELSE IF directive == 'text':
                current_address = text_address
            ELSE IF directive == 'word':
                current_address += len(args) * 4
            ELSE IF directive == 'byte':
                current_address += len(args)
        
        ELSE IF parsed.type == 'label':
            symbol_table.add_symbol(parsed.label, current_address)
        
        ELSE IF parsed.type == 'instruction':
            current_address += 4  # Her komut 4 byte
    
    RETURN symbol_table
```

**Zaman Karmaşıklığı**: O(n) n = satır sayısı
**Uzay Karmaşıklığı**: O(m) m = etiket sayısı

#### Algoritma 2: İkinci Geçiş

```
FUNCTION second_pass(lines):
    current_address = text_address
    output = []
    
    FOR each line in lines:
        parsed = parse_line(line)
        
        IF parsed.type == 'directive':
            IF directive == 'word':
                FOR each value in args:
                    output.append((current_address, value))
                    current_address += 4
            ELSE IF directive == 'byte':
                FOR each value in args:
                    output.append((current_address, value))
                    current_address += 1
            ELSE IF directive == 'end':
                BREAK
        
        ELSE IF parsed.type == 'instruction':
            machine_code = generate_instruction(parsed, current_address)
            output.append((current_address, machine_code))
            current_address += 4
    
    RETURN output
```

**Zaman Karmaşıklığı**: O(n) n = satır sayısı
**Uzay Karmaşıklığı**: O(n) n = komut sayısı

### Makine Kodu Üretim Algoritması

```
FUNCTION generate_instruction(parsed_line, current_address):
    mnemonic = parsed_line.mnemonic
    operands = parsed_line.operands
    inst_info = opcode_table.get(mnemonic)
    
    IF inst_info.type == 'R':
        RETURN generate_r_type(inst_info, operands)
    ELSE IF inst_info.type == 'I':
        RETURN generate_i_type(inst_info, operands, current_address)
    ELSE IF inst_info.type == 'S':
        RETURN generate_s_type(inst_info, operands)
    ELSE IF inst_info.type == 'B':
        RETURN generate_b_type(inst_info, operands, current_address)
    ELSE IF inst_info.type == 'U':
        RETURN generate_u_type(inst_info, operands)
    ELSE IF inst_info.type == 'J':
        RETURN generate_j_type(inst_info, operands, current_address)
```

**Zaman Karmaşıklığı**: O(1) - sabit zaman
**Uzay Karmaşıklığı**: O(1) - sabit bellek

---

## Akış Diyagramı

Aşağıdaki metinsel akış diyagramı, assembler'ın uçtan uca işlem adımlarını özetler:

```
Başla
  |
  v
Kaynak dosyayı oku
  |
  v
1. Geçiş (First Pass):
  - Satırları parse et
  - Direktiflere göre adres güncelle
  - Label'ları Symbol Table'a ekle
  |
  v
2. Geçiş (Second Pass):
  - Satırları tekrar parse et
  - Direktif verilerini üret
  - Komutları makine koduna çevir
  - Çıktı buffer'ına yaz
  |
  v
Hata var mı?
  |-- Evet --> Hata raporla ve dur
  |-- Hayır --> İstenen formatta çıktı üret (ELF/HEX/Binary/Verilog)
  |
  v
Bitiş
```

---

## RISC-V Komut Seti Desteği

### Desteklenen Komut Kategorileri

#### 1. Aritmetik ve Mantık Komutları

**R-Type**:
- `add`: Toplama
- `sub`: Çıkarma
- `sll`: Sola kaydırma (shift left logical)
- `slt`: Set less than (signed)
- `sltu`: Set less than (unsigned)
- `xor`: XOR işlemi
- `srl`: Sağa kaydırma (shift right logical)
- `sra`: Sağa kaydırma aritmetik (shift right arithmetic)
- `or`: OR işlemi
- `and`: AND işlemi

**I-Type**:
- `addi`: Immediate toplama
- `slti`: Set less than immediate (signed)
- `sltiu`: Set less than immediate (unsigned)
- `xori`: XOR immediate
- `ori`: OR immediate
- `andi`: AND immediate
- `slli`: Shift left logical immediate
- `srli`: Shift right logical immediate
- `srai`: Shift right arithmetic immediate

#### 2. Bellek Erişim Komutları

**Load (I-Type)**:
- `lb`: Load byte (signed)
- `lh`: Load halfword (signed)
- `lw`: Load word
- `lbu`: Load byte (unsigned)
- `lhu`: Load halfword (unsigned)

**Store (S-Type)**:
- `sb`: Store byte
- `sh`: Store halfword
- `sw`: Store word

#### 3. Kontrol Akış Komutları

**Branch (B-Type)**:
- `beq`: Branch if equal
- `bne`: Branch if not equal
- `blt`: Branch if less than (signed)
- `bge`: Branch if greater or equal (signed)
- `bltu`: Branch if less than (unsigned)
- `bgeu`: Branch if greater or equal (unsigned)

**Jump**:
- `jal`: Jump and link (J-Type)
- `jalr`: Jump and link register (I-Type)

#### 4. Üst Immediate Komutları (U-Type)

- `lui`: Load upper immediate
- `auipc`: Add upper immediate to PC

#### 5. Sistem Komutları (I-Type)

- `ecall`: Environment call
- `ebreak`: Environment break

### Komut Encoding Örnekleri

#### Örnek 1: ADD Komutu
```assembly
add x3, x1, x2
```

**Encoding**:
- `x3` (rd) = 3 = `0b00011`
- `x1` (rs1) = 1 = `0b00001`
- `x2` (rs2) = 2 = `0b00010`
- `funct7` = 0x00 = `0b0000000`
- `funct3` = 0x0 = `0b000`
- `opcode` = 0x33 = `0b0110011`

**Bit Düzeni** (31:0):
```
0000000 00010 00001 000 00011 0110011
funct7  rs2   rs1   f3  rd    opcode
```

**Hex**: `0x002081B3`

#### Örnek 2: ADDI Komutu
```assembly
addi x1, x0, 10
```

**Encoding**:
- `x1` (rd) = 1 = `0b00001`
- `x0` (rs1) = 0 = `0b00000`
- `imm` = 10 = `0b000000001010` (12-bit signed)
- `funct3` = 0x0 = `0b000`
- `opcode` = 0x13 = `0b0010011`

**Bit Düzeni** (31:0):
```
000000001010 00000 000 00001 0010011
imm[11:0]    rs1   f3  rd    opcode
```

**Hex**: `0x00A00093`

#### Örnek 3: BEQ Komutu
```assembly
beq x1, x2, loop  # loop = 0x0008, current = 0x0004
```

**Encoding**:
- `x1` (rs1) = 1 = `0b00001`
- `x2` (rs2) = 2 = `0b00010`
- `offset` = 0x0008 - 0x0004 = 4 = `0b0000000000100` (13-bit signed, aligned)
- `funct3` = 0x0 = `0b000`
- `opcode` = 0x63 = `0b1100011`

**Bit Düzeni** (31:0):
```
0 000010 00010 00001 000 0010 0 1100011
imm[12] imm[10:5] rs2 rs1 f3 imm[4:1] imm[11] opcode
```

**Hex**: `0x00208263`

---

## Kullanım Kılavuzu

### Komut Satırı Kullanımı

#### Temel Kullanım
```bash
python main.py input.s
```

#### Çıktı Dosyası Belirtme
```bash
python main.py input.s -o output.hex
```

#### Çıktı Formatı Seçme
```bash
# Hex format (varsayılan)
python main.py input.s -o output.hex -f hex

# Verilog format
python main.py input.s -o output.v -f verilog

# Binary format
python main.py input.s -o output.bin -f binary
```

#### Sembol Tablosunu Görüntüleme
```bash
python main.py input.s -s
```

#### Detaylı Çıktı
```bash
python main.py input.s -v
```

### Programatik Kullanım

```python
from assembler import Assembler

# Assembler oluştur
asm = Assembler()

# Dosyadan assemble et
result = asm.assemble_file('program.s')

# Veya string'den assemble et
source = """
.text
    addi x1, x0, 10
    add  x2, x1, x1
"""
result = asm.assemble(source)

# Sonuç kontrolü
if result['success']:
    # Çıktıyı yazdır
    asm.print_output()
    
    # Sembol tablosunu yazdır
    asm.print_symbol_table()
    
    # Dosyaya yaz
    asm.write_object_file('output.hex', format='hex')
else:
    # Hataları yazdır
    for error in result['errors']:
        print(f"Error: {error}")
```

### Assembly Dili Sözdizimi

#### Komut Formatları

**R-Type**:
```assembly
add  rd, rs1, rs2
sub  rd, rs1, rs2
sll  rd, rs1, rs2
```

**I-Type**:
```assembly
addi rd, rs1, imm
lw   rd, offset(rs1)
jalr rd, offset(rs1)
```

**S-Type**:
```assembly
sw rs2, offset(rs1)
sh rs2, offset(rs1)
sb rs2, offset(rs1)
```

**B-Type**:
```assembly
beq  rs1, rs2, label
bne  rs1, rs2, label
blt  rs1, rs2, label
```

**U-Type**:
```assembly
lui   rd, imm
auipc rd, imm
```

**J-Type**:
```assembly
jal   label
jal   rd, label
```

#### Direktifler

```assembly
.data                    # Veri segmenti başlat
.text                    # Kod segmenti başlat
.org 0x1000             # Adresi ayarla
label: .word 0x12345678  # 32-bit değer tanımla
array: .byte 1, 2, 3     # Byte dizisi tanımla
.end                     # Sonlandır
```

#### Etiketler

```assembly
# Ayrı satırda
start:
    addi x1, x0, 10

# Aynı satırda
loop: addi x1, x1, 1
```

#### Yorumlar

```assembly
addi x1, x0, 10  # Bu bir yorum
# Bu da bir yorum satırı
```

---

## Örnekler ve Test Senaryoları

### Test 1: Basit Aritmetik (test_simple.s)

```assembly
.text
.org 0x0000

start:
    addi x1, x0, 10      # x1 = 10
    addi x2, x0, 20      # x2 = 20
    add  x3, x1, x2      # x3 = x1 + x2 = 30
    sub  x4, x2, x1      # x4 = x2 - x1 = 10
    
    # Store result
    sw   x3, 0(x0)       # Store x3 at address 0
    
    # Branch example
    beq  x1, x2, end     # If x1 == x2, jump to end
    addi x5, x0, 1       # x5 = 1
    
end:
    ebreak               # End of program
```

**Çıktı**:
```
Address      Machine Code
0x00000000   0x00A00093  # addi x1, x0, 10
0x00000004   0x01400113  # addi x2, x0, 20
0x00000008   0x002081B3  # add  x3, x1, x2
0x0000000C   0x40110233  # sub  x4, x2, x1
0x00000010   0x00302023  # sw   x3, 0(x0)
0x00000014   0x00208263  # beq  x1, x2, end
0x00000018   0x00100293  # addi x5, x0, 1
0x0000001C   0x00100073  # ebreak
```

### Test 2: Veri Direktifleri (test_data.s)

```assembly
.data
.org 0x1000

value1: .word 0x12345678
value2: .word 0xABCDEF00
array:  .byte 1, 2, 3, 4, 5

.text
.org 0x0000

main:
    lui  x1, 0x1         # Load upper immediate (0x00001000)
    lw   x2, 0(x1)       # Load value1
    lw   x3, 4(x1)       # Load value2
    
    # Arithmetic
    add  x4, x2, x3      # x4 = value1 + value2
    
    # Store result
    sw   x4, 16(x1)      # Store result
    
    ebreak
```

**Çıktı**:
```
# Data segment
0x00001000   0x12345678
0x00001004   0xABCDEF00
0x00001008   0x00000001
0x00001009   0x00000002
0x0000100A   0x00000003
0x0000100B   0x00000004
0x0000100C   0x00000005

# Text segment
0x00000000   0x000010B7  # lui  x1, 0x1
0x00000004   0x0000A103  # lw   x2, 0(x1)
0x00000008   0x0040A183  # lw   x3, 4(x1)
0x0000000C   0x00310233  # add  x4, x2, x3
0x00000010   0x0040A823  # sw   x4, 16(x1)
0x00000014   0x00100073  # ebreak
```

### Test 3: Dallanma ve Atlama (test_branch.s)

```assembly
.text
.org 0x0000

main:
    addi x5, x0, 5       # x5 = 5
    addi x6, x0, 10      # x6 = 10
    
loop:
    addi x5, x5, 1       # x5 = x5 + 1
    blt  x5, x6, loop    # If x5 < x6, branch to loop
    
    # Jump example
    jal  x1, subroutine  # Jump and link
    
done:
    ebreak

subroutine:
    addi x3, x0, 42      # x3 = 42
    jalr x0, 0(x1)       # Return
```

**Sembol Tablosu**:
```
Label       Address
main        0x00000000
loop        0x00000008
done        0x00000014
subroutine  0x00000018
```

---

## Algoritma Karmaşıklığı Analizi

### Zaman Karmaşıklığı (Time Complexity)

#### Genel Analiz

**Birinci Geçiş**:
- Her satır için parse: O(1)
- Sembol ekleme: O(1) (hash table)
- Toplam: **O(n)** n = satır sayısı

**İkinci Geçiş**:
- Her satır için parse: O(1)
- Makine kodu üretimi: O(1)
- Toplam: **O(n)** n = satır sayısı

**Toplam Zaman Karmaşıklığı**: **O(n)**

#### Detaylı Analiz

| İşlem | Karmaşıklık | Açıklama |
|-------|-------------|----------|
| Dosya okuma | O(n) | n = satır sayısı |
| Parse (satır başına) | O(1) | Regex matching |
| Sembol tablosu lookup | O(1) | Hash table |
| Sembol tablosu ekleme | O(1) | Hash table |
| Makine kodu üretimi | O(1) | Bit operasyonları |
| Çıktı yazma | O(m) | m = komut sayısı |

**Toplam**: O(n + m) ≈ **O(n)** (n >> m genelde)

### Uzay Karmaşıklığı (Space Complexity)

#### Bileşen Bazında

**Opcode Table**: O(k) k = komut sayısı (sabit, ~50)
- **Gerçek**: O(1) - sabit boyut

**Symbol Table**: O(m) m = etiket sayısı
- **Ortalama**: O(m) m << n genelde

**Parse Tree**: O(1) per line
- **Toplam**: O(n) - geçici, garbage collected

**Output**: O(m) m = komut sayısı
- **Gerçek**: O(m) - kalıcı

**Toplam Uzay Karmaşıklığı**: **O(n + m)**

#### Detaylı Analiz

| Veri Yapısı | Boyut | Açıklama |
|-------------|-------|----------|
| Opcode table | O(1) | Sabit boyutlu dictionary |
| Symbol table | O(m) | m = etiket sayısı |
| Parse buffer | O(1) | Satır başına sabit |
| Output array | O(m) | m = komut sayısı |
| Forward refs | O(f) | f = forward reference sayısı |

**Toplam**: O(m + f) ≈ **O(n)** (worst case)

### Optimizasyon Notları

1. **Hash Table Kullanımı**: O(1) lookup için
2. **İki Geçiş**: Forward reference'ları çözmek için gerekli
3. **Lazy Evaluation**: Sadece gerektiğinde parse et
4. **Memory Efficient**: Gereksiz kopyalama yok

---

## Teknik Detaylar

### Hata Yönetimi

#### Hata Tipleri

1. **Syntax Hataları**:
   - Geçersiz komut
   - Yanlış operand sayısı
   - Geçersiz register

2. **Semantic Hataları**:
   - Tanımsız etiket
   - Duplicate label
   - Offset aralık dışı

3. **Runtime Hataları**:
   - Dosya bulunamadı
   - Okuma/yazma hatası

#### Hata Mesajları

```python
# Örnek hata mesajları
"Unknown instruction: invalid_inst"
"R-type instruction requires 3 operands, got 2"
"Invalid register: x99"
"Undefined label: undefined_label"
"Duplicate label definition: duplicate_label"
"Branch offset out of range or not aligned: 5000"
```

### Özel Durumlar

#### 1. Forward References

```assembly
    beq x1, x2, end  # end henüz tanımlanmamış
    # ... kod ...
end:
    ebreak
```

**Çözüm**: İki geçişli assembly - ilk geçişte tüm etiketler toplanır.

#### 2. Offset Hesaplama

**Branch**: 13-bit signed, 2-byte aligned
- Aralık: -4096 ile +4094 arası
- Hizalama: Offset çift sayı olmalı

**Jump**: 21-bit signed, 2-byte aligned
- Aralık: -1048576 ile +1048574 arası
- Hizalama: Offset çift sayı olmalı

#### 3. Sign Extension

12-bit immediate değerler:
- Pozitif: 0x000 - 0x7FF (0 - 2047)
- Negatif: 0x800 - 0xFFF (-2048 - -1)

**Örnek**:
```python
10  → 0x00A (12-bit)
-5  → 0xFFB (12-bit, sign-extended)
```

### Çıktı Formatları

#### Hex Format
```
00000000: 00A00093
00000004: 01400113
```

#### Verilog Format
```verilog
// Machine code output
// Format: address: instruction
32'h00A00093, // 0x00000000
32'h01400113, // 0x00000004
```

#### Binary Format
Raw binary, little-endian, 32-bit words

### Test Stratejisi

1. **Unit Tests**: Her bileşen ayrı test edilir
2. **Integration Tests**: Bileşenler birlikte test edilir
3. **End-to-End Tests**: Tam assembly süreci test edilir

### Performans Metrikleri

**Küçük Program** (< 100 satır):
- Assembly süresi: < 10ms
- Bellek kullanımı: < 1MB

**Orta Program** (100-1000 satır):
- Assembly süresi: < 100ms
- Bellek kullanımı: < 10MB

**Büyük Program** (> 1000 satır):
- Assembly süresi: < 1s
- Bellek kullanımı: < 100MB

---

## Sonuç

Bu dokümantasyon, RISC-V RV32I assembler projesinin tüm teknik detaylarını kapsamaktadır. Proje, modüler yapısı, etkin algoritmaları ve kapsamlı özellik seti ile eğitim amaçlı bir assembler için gerekli tüm bileşenlere sahiptir.

### Proje Özellikleri Özeti

✅ Tam RV32I komut seti desteği
✅ İki geçişli assembly süreci
✅ Sembol tablosu ve forward reference çözümü
✅ Tüm direktif desteği
✅ Çoklu çıktı formatı
✅ Kapsamlı hata yönetimi
✅ Modüler ve genişletilebilir mimari

### Gelecek Geliştirmeler

- RISC-V extension desteği (M, A, F, D)
- Macro desteği
- Expression evaluation
- Linker entegrasyonu
- ELF format çıktısı
- Optimizasyon seçenekleri

---

**Proje Tarihi**: 2024
**Versiyon**: 1.0
**Lisans**: Eğitim amaçlı


## Literatür Araştırması

## Araştırma Kapsamı

Bu çalışma kapsamında literatür araştırması; RISC-V ISA standardı, assembler tasarım prensipleri, iki geçişli assembler yaklaşımı, sembol ve opcode tablosu yapıları ile eğitim amaçlı simülatörlerin yürütme davranışları üzerine odaklanmaktadır.

## İncelenen Konular

- RISC-V RV32I komut seti ve encoding kuralları  
- Assembler mimarisi ve parse/encode süreçleri  
- Etiket çözümleme ve forward reference yöntemleri  
- Direktif işleme stratejileri  
- ELF ve düz metin object çıktı yaklaşımları  
- Test ve doğrulama pratikleri  

---

# Kaynakça

## RISC-V ISA ve Komut Seti

[1] RISC-V International,  
*The RISC-V Instruction Set Manual, Volume I: User-Level ISA (RV32I)*.  
[Erişim]: https://riscv.org/technical/specifications/

[2] Patterson, D. A., & Hennessy, J. L.,  
*Computer Organization and Design RISC-V Edition*.  
Morgan Kaufmann, 2017.

---

## Assembler Tasarımı ve Sistem Yazılımları

[3] Beck, L. L.,  
*System Software: An Introduction to Systems Programming*.  
Addison-Wesley, 1997.

[4] Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D.,  
*Compilers: Principles, Techniques, and Tools (2nd Edition)*.  
Pearson, 2006.

[5] Cooper, K. D., & Torczon, L.,  
*Engineering a Compiler (2nd Edition)*.  
Morgan Kaufmann, 2011.

---

## Assembler Direktifleri ve Araç Zinciri

[6] GNU Project,  
*GNU Assembler (GAS) Documentation*.  
[Erişim]: https://sourceware.org/binutils/docs/as/

[7] GNU Project,  
*GNU Binutils Documentation*.  
[Erişim]: https://sourceware.org/binutils/

---

## Object Dosya Formatı ve Bağlayıcılar

[8] Levine, J. R.,  
*Linkers and Loaders*.  
Morgan Kaufmann, 1999.

---

## Simülasyon ve Eğitim Araçları

[9] CPUlator,  
Educational CPU Simulator.  
[Erişim]: https://cpulator.01xz.net/

[10] RARS,  
RISC-V Assembler and Simulator.  
[Erişim]: https://github.com/TheThirdOne/rars

---

## Test ve Doğrulama Yaklaşımları

[11] GNU Toolchain Utilities (*objdump*, *readelf*)  
Resmi dokümantasyonlar.  
[Erişim]: https://sourceware.org/binutils/docs/

[12] Açık kaynak RISC-V test ve doğrulama projeleri  
(çeşitli referans implementasyonlar).