# HUONG DAN SU DUNG PHAN MEM LCC HVAC FILTER

Tai lieu nay mo ta cach su dung phan mem **LCC HVAC Filter System** de tinh toan Life Cycle Cost / Total Cost of Ownership cho he thong loc gio HVAC/AHU.

Phan mem duoc xay dung bang Python va Streamlit. Nguoi dung co the chay tren may tinh ca nhan hoac truy cap bang link online neu app da duoc deploy tren Streamlit Community Cloud.

## 1. Muc Dich Cua Phan Mem

Phan mem dung de so sanh chi phi vong doi cua cac phuong an loc gio, bao gom:

- Chi phi mua loc moi moi nam.
- Chi phi dien nang do tro luc loc.
- Chi phi nhan cong thay loc.
- Chi phi xu ly loc thai bo.
- Chi phi downtime neu co.
- Phat thai CO2 moi nam.
- Tong chi phi TCO/year cua tung phuong an.
- Tien tiet ki cua tung Option so voi Base / Current.
- Lua chon Option tot nhat dua tren TCO/year thap nhat.

## 2. Cach Mo Phan Mem

### 2.1. Chay Tren May Windows

Mo thu muc du an, sau do double-click file:

```text
lcc_hvac_app/run_app.bat
```

Neu chay bang PowerShell, dung lenh:

```powershell
lcc_hvac_app\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Sau khi app chay, mo trinh duyet tai dia chi:

```text
http://localhost:8501
```

### 2.2. Chay Tren MacBook

Lan dau tien, mo Terminal trong thu muc du an va chay:

```bash
chmod +x lcc_hvac_app/run_app_mac.command
```

Sau do double-click:

```text
lcc_hvac_app/run_app_mac.command
```

### 2.3. Chay Online Bang Streamlit Cloud

Neu du an da duoc dua len GitHub va deploy tren Streamlit Cloud, nguoi dung chi can mo link app tren trinh duyet. Khong can cai Python, VS Code, hay bat ky moi truong lap trinh nao.

## 3. Tong Quan Menu Cua App

Menu ben trai cua app gom 5 phan chinh:

```text
1. Project Setup
2. Filter Data
3. Scenarios
4. Analysis
5. Export
```

Moi phan co mot vai tro rieng trong quy trinh tinh LCC.

## 4. Project Setup

Phan nay dung de nhap thong tin du an va cac gia dinh van hanh.

### 4.1. Project Info

Nhap cac thong tin chung:

- **Project Name**: Ten du an.
- **Customer**: Ten khach hang.
- **Location**: Dia diem nha may / AHU.
- **Engineer**: Nguoi thuc hien tinh toan.
- **Date**: Ngay lap tinh toan.
- **Currency**: Don vi tien te, vi du `VND`.

Cac thong tin nay se hien thi tren dashboard va duoc xuat ra file Excel report.

### 4.2. Operating Assumptions

Nhap cac thong so van hanh:

- **Airflow m3/h per AHU**: Luu luong gio cua moi AHU.
- **Number of AHU**: So luong AHU.
- **Operating hours/day**: So gio hoat dong moi ngay.
- **Operating days/year**: So ngay hoat dong moi nam.
- **Fan efficiency**: Hieu suat quat.
- **Electricity price VND/kWh**: Gia dien.
- **Dust concentration mg/m3**: Nong do bui dau vao.
- **Environment factor**: He so moi truong.
- **Labor cost/filter change**: Chi phi nhan cong cho moi lan thay loc.
- **Disposal cost/filter change**: Chi phi xu ly loc thai bo.
- **Downtime cost/change**: Chi phi dung may moi lan thay loc, neu co.
- **CO2 emission factor kg/kWh**: He so phat thai CO2 cua dien nang.
- **Analysis period years**: So nam phan tich.

Luu y: cac gia tri nay anh huong truc tiep den ket qua TCO, energy cost, replacement/year va CO2/year.

## 5. Filter Data

Phan nay dung de tao, import, sua, xoa va quan ly database cua filter.

### 5.1. Upload Excel Filter Database

Nguoi dung co the upload file Excel:

```text
.xlsx, .xlsm, .xls
```

Neu workbook co sheet ten:

```text
Filter_Database
```

app se uu tien chon sheet nay de import.

Sau khi upload:

1. Chon sheet can import.
2. Bam **Import selected sheet**.
3. Du lieu se duoc dua vao bang Filter Records.

### 5.2. Add Or Update One Filter Record

Day la form chinh de tao filter moi hoac sua filter co san.

Thong tin can nhap:

- **Filter ID**: Ma filter, vi du `PF-001`, `FF-001`, `HEPA-001`.
- **Supplier**: Nha cung cap.
- **Filter Type**: Loai loc, vi du Panel filter, Bag filter, HEPA filter.
- **Stage**: Vi tri loc, vi du Pre-filter, Fine-filter, HEPA.
- **Model**: Ten model.
- **Size**: Kich thuoc loc.
- **ISO Class**: Cap loc theo ISO hoac EN.
- **DHC (g)**: Dust Holding Capacity.
- **Mass Efficiency**: Hieu suat khoi luong. Co the nhap `0.85` hoac `85`.
- **Initial DP (Pa)**: Tro luc dau.
- **Avg DP (Pa)**: Tro luc trung binh dung de tinh energy cost.
- **Final DP (Pa)**: Tro luc cuoi.
- **Price/filter**: Gia moi filter.
- **Notes**: Ghi chu, khong bat buoc.

Nut **Save filter record** chi duoc bam khi cac truong bat buoc da duoc nhap day du va cac gia tri so lon hon 0.

Neu **Filter ID** da ton tai, app se update record cu. Neu **Filter ID** chua ton tai, app se tao record moi.

### 5.3. Sua Mot Dong Trong Filter Records

Co 2 cach sua du lieu filter.

Cach 1:

1. Tai form **Add or update one filter record**.
2. Chon **Edit existing filter**.
3. Chon Filter ID can sua.
4. Sua cac gia tri trong form.
5. Bam **Save filter record**.

Cach 2:

1. Xem bang **Filter Records**.
2. Mo khung **Modify a row from Filter Records**.
3. Chon Filter ID can sua.
4. Bam **Edit selected row**.
5. Record se duoc load len form o phia tren.
6. Sua gia tri.
7. Bam **Save filter record**.

### 5.4. Xoa Filter Records

Co 2 cach xoa:

- Xoa mot record dang duoc chon trong form bang nut **Delete selected filter record**.
- Xoa mot hoac nhieu record trong khung **Delete filter records**.

Quy trinh xoa nhieu dong:

1. Mo **Delete filter records**.
2. Chon mot hoac nhieu Filter ID.
3. Bam **Delete selected rows**.

### 5.5. Download Database

Co 2 nut download:

- **Download database CSV**: Tai database duoi dang CSV.
- **Download database Excel**: Tai database duoi dang Excel `.xlsx`.

File Excel export co sheet:

```text
Filter_Database
```

### 5.6. Luu Y Khi Chay Online

Khi chay tren Streamlit Cloud, user co the upload, sua va download Excel. Tuy nhien, Streamlit Community Cloud khong phai la database server de luu thay doi vinh vien cho tat ca user.

Neu muon moi user cung sua chung mot database online, nen ket noi app voi:

- Google Sheets.
- Supabase.
- PostgreSQL.
- Airtable.
- SharePoint / OneDrive API.

## 6. Scenarios

Phan Scenarios dung de tao va so sanh Base / Current voi cac Option.

### 6.1. Base / Current

Day la phuong an hien tai cua khach hang. App dung Base / Current lam moc so sanh voi cac Option.

Base / Current khong nen xoa, vi can dung de tinh:

- Saving/year.
- Saving %.
- Option tot nhat.

### 6.2. Option 1, Option 2, Option 3 Va Cac Option Moi

Nguoi dung co the:

- Them option bang **Add Option**.
- Xoa option bang **Remove Option**.
- Copy du lieu tu Base bang **Copy from Base**.
- Copy tu option truoc do bang **Copy from Previous Option**.
- Xoa stage trong option bang **Remove**.
- Them stage bang **Add Stage**.

Tat ca option duoc tao moi se tu dong xuat hien trong:

- Dashboard.
- TCO Model.
- Detailed Results.
- Excel Export.

### 6.3. Chon Filter ID Tu Filter Data

Trong moi stage, co dropdown:

```text
Select Filter ID from Filter Data
```

Neu chon mot Filter ID, app se load thong so filter tu Filter Data vao stage:

- Stage.
- DHC.
- Mass Efficiency.
- Avg DP.
- Price/filter.

Sau khi load, nguoi dung van co the sua thu cong tung gia tri trong stage.

Nut **Reload parameters from selected filter** dung de nap lai thong so tu database neu nguoi dung da sua nham.

### 6.4. Thong So Moi Stage

Moi stage gom:

- **Stage**: Ten cap loc.
- **Quantity per AHU**: So luong filter moi AHU.
- **Dust Holding Capacity (g)**: Suc chua bui.
- **Mass Efficiency**: Hieu suat bat bui.
- **Average Pressure Drop (Pa)**: Tro luc trung binh.
- **Price per Filter**: Gia moi filter.

## 7. Eurovent Average DP Calculator

Trong Scenarios, moi stage co phan tinh Average DP theo Eurovent 4/21.

Nguoi dung co the nhap:

- **ISO Group**: ISO ePM1, ISO ePM2.5, ISO ePM10, ISO Coarse.
- **Mx (g)**: Gia tri bui toi han theo ISO group.
- Bang du lieu curve gom:
  - Dust fed mi (g).
  - Pressure drop dPi (Pa).

Cong thuc:

```text
Eurovent Avg DP = SUM(dmi x Segment average DP) / Mx
```

Trong do:

```text
dmi = MIN(current dust fed, Mx) - MIN(previous dust fed, Mx)
Segment average DP = (current DP + previous DP) / 2
```

Sau khi tinh, bam:

```text
Apply Eurovent Avg DP to this stage
```

de dua ket qua vao **Average Pressure Drop (Pa)** cua stage.

## 8. Analysis

Phan Analysis gom 3 tab:

```text
Dashboard
TCO Model
Detailed Results
```

### 8.1. Dashboard

Dashboard hien thi KPI va bieu do tong quan:

- **Base TCO/year**: Tong chi phi nam cua Base / Current.
- **Best option**: Phuong an co TCO/year thap nhat.
- **Saving/year**: Tien tiet ki moi nam so voi Base.
- **CO2/year**: Phat thai CO2 moi nam.
- Bieu do TCO/year theo scenario.
- Bieu do cost breakdown.
- Bieu do CO2.
- Bieu do stage-level TCO theo Pre-filter, Fine-filter, HEPA hoac cac stage khac.

Dashboard dung de trinh bay nhanh cho sep hoac khach hang.

### 8.2. TCO Model

Tab TCO Model hien thi bang tinh chi tiet theo tung stage:

- Scenario.
- Filter Stage.
- Qty/AHU.
- DHC.
- Mass Efficiency.
- Avg DP.
- Dust Entering.
- Dust Captured.
- Filter Life.
- Replacement/year.
- Filter Cost/year.
- Energy kWh/year.
- Energy Cost/year.
- Labor + Disposal/year.
- CO2 kg/year.
- TCO/year.

Nguoi dung co the download file CSV cua TCO model bang:

```text
Download TCO model CSV
```

### 8.3. Detailed Results

Detailed Results hien thi cac bang audit chi tiet de kiem tra ket qua tinh:

- Ket qua tong hop theo scenario.
- Ket qua theo tung stage.
- So sanh voi Base / Current.

Phan nay phu hop khi can kiem tra so lieu truoc khi gui report cho khach hang.

## 9. Export

Phan Export dung de luu va tai ket qua.

### 9.1. Save Project JSON

Nut **Save Project JSON** dung de luu toan bo project:

- Project Info.
- Operating Assumptions.
- Filter Database.
- Scenarios.
- Ket qua tinh.

File JSON giup nguoi dung mo lai project sau nay.

### 9.2. Load Project JSON

Dung **Load Project JSON** de tai lai project da luu.

Quy trinh:

1. Vao Export.
2. Upload file JSON da luu.
3. App se nap lai thong tin project.

### 9.3. Export Excel Report

Nut **Export Excel Report** tao file Excel report cho khach hang.

File Excel co cac sheet chinh:

- Project Summary.
- Assumptions.
- Scenario Inputs.
- Results.
- Chart Data.
- Formula Reference.
- Filter Database.

Excel report co du lieu va chart de gui cho khach hang.

### 9.4. Reset Input

Nut **Reset Input** tao lai project moi va xoa input hien tai trong session. Chi dung khi muon bat dau tinh toan tu dau.

## 10. Cac Cong Thuc Chinh

### 10.1. Dust Entering

```text
Dust entering = Airflow x Dust concentration x Environment factor x Operating hours/day / 1000 / Qty per AHU
```

Don vi:

```text
g/day/filter
```

### 10.2. Dust Captured

```text
Dust captured = Dust entering x Mass efficiency
```

### 10.3. Dust To Next Stage

```text
Dust to next stage = Dust entering - Dust captured
```

### 10.4. Filter Life

```text
Filter life = Dust holding capacity / Dust captured
```

Don vi:

```text
days
```

### 10.5. Replacement Per Year

```text
Replacement/year = Operating days/year / Filter life
```

### 10.6. Filter Cost Per Year

```text
Filter cost/year = Replacement/year x Price/filter x Qty per AHU x Number of AHU
```

### 10.7. Energy kWh Per Year

```text
Energy kWh/year = (Airflow / 3600) x Average pressure drop x Operating hours/year / (1000 x Fan efficiency) x Number of AHU
```

### 10.8. Energy Cost Per Year

```text
Energy cost/year = Energy kWh/year x Electricity price
```

### 10.9. Labor + Disposal Cost Per Year

```text
Labor + disposal/year =
Replacement/year x Qty per AHU x (Labor cost + Disposal cost) x Number of AHU
+ Replacement/year x Downtime cost x Number of AHU
```

### 10.10. CO2 Per Year

```text
CO2/year = Energy kWh/year x CO2 emission factor
```

### 10.11. TCO Per Year

```text
TCO/year = Filter cost/year + Energy cost/year + Labor + disposal/year
```

### 10.12. Saving Per Year

```text
Saving/year = Base TCO/year - Option TCO/year
```

### 10.13. Saving %

```text
Saving % = Saving/year / Base TCO/year x 100
```

### 10.14. Best Option

```text
Best option = Scenario with the lowest TCO/year
```

## 11. Cach Kiem Tra Ket Qua

De kiem tra cong thuc va ket qua:

1. Vao **Analysis**.
2. Mo **TCO Model**.
3. Xem bang stage-by-stage.
4. Mo **Formula Reference**.
5. So sanh tung dong voi cong thuc trong phan 10 cua tai lieu nay.
6. Export Excel Report de xem lai bang ket qua va chart data.

Neu can audit chi tiet, nen dung tab **Detailed Results** va file Excel export.

## 12. Cach Cap Nhat App Sau Khi Sua Code

Neu sua app tren laptop:

1. Sua code trong thu muc local.
2. Chay test:

```powershell
lcc_hvac_app\.venv\Scripts\python.exe -m pytest lcc_hvac_app\tests
```

3. Chay app de kiem tra:

```powershell
lcc_hvac_app\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

4. Push len GitHub branch:

```text
full-app
```

5. Streamlit Cloud se tu dong redeploy neu app dang connect voi branch nay.

## 13. Cac File Quan Trong Trong Du An

```text
streamlit_app.py
```

File entrypoint dung cho Streamlit Cloud.

```text
requirements.txt
```

Danh sach package can cai khi deploy online.

```text
lcc_hvac_app/app.py
```

File chinh dieu khien layout, sidebar, menu va routing cua app.

```text
lcc_hvac_app/ui/
```

Thu muc giao dien nguoi dung.

```text
lcc_hvac_app/engine/
```

Thu muc cong thuc va logic tinh toan.

```text
lcc_hvac_app/export/export_excel.py
```

File tao Excel report.

```text
lcc_hvac_app/data/filter_database.csv
```

Database filter mac dinh cua app.

```text
lcc_hvac_app/tests/
```

Thu muc test de kiem tra cong thuc va chuc nang.

## 14. Luu Y Khi Nhap Du Lieu

- Khong nen de DHC bang 0.
- Khong nen de Avg DP bang 0 neu can tinh energy cost.
- Fan efficiency phai lon hon 0.
- Operating days/year va operating hours/day phai lon hon 0.
- Mass Efficiency co the nhap `0.85` hoac `85`; app se tu dong chuan hoa neu gia tri lon hon 1.
- Base / Current nen dai dien dung he thong hien tai cua khach hang.
- Option nen dai dien tung phuong an de xuat khac nhau.

## 15. Quy Trinh De Xuat Khi Lam Mot Project Moi

1. Vao **Project Setup** va nhap thong tin du an.
2. Nhap **Operating Assumptions**.
3. Vao **Filter Data** va import database filter hoac tao filter moi.
4. Vao **Scenarios**.
5. Nhap Base / Current.
6. Tao cac Option can so sanh.
7. Chon Filter ID tu Filter Data cho tung stage neu co.
8. Bam **Calculate** o sidebar.
9. Vao **Analysis** de xem Dashboard, TCO Model va Detailed Results.
10. Vao **Export** de luu Project JSON va xuat Excel Report.

## 16. Ket Luan

Phan mem nay giup chuan hoa qua trinh tinh LCC cho he thong filter HVAC/AHU. Nguoi dung co the quan ly database filter, tao nhieu phuong an, so sanh chi phi va xuat report Excel de gui cho khach hang.

Khi can thay doi UI, cong thuc, dashboard, filter database, export Excel hoac workflow online, nen cap nhat code tren laptop, test lai va push len GitHub branch `full-app`.
