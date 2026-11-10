# Boab Ridge Mining Services: organisation chart

Generated from the `manager` column of `lab/data/users.csv` by `scripts/gen-org-chart.py`. 60 people, all fictional. Dark boxes are the Perth head office, light boxes the remote site office.

```mermaid
flowchart TB
  n_margaret_osei["Margaret Osei<br/>General Manager"]:::perth
  n_alice["Alice Nguyen<br/>Executive Assistant"]:::perth
  n_gail_sutherland["Gail Sutherland<br/>Office Manager"]:::perth
  n_hamish_mcleod["Hamish McLeod<br/>Receptionist"]:::perth
  n_sofia_rossi["Sofia Rossi<br/>Administration Officer"]:::perth
  n_tyler_barnes["Tyler Barnes<br/>Trainee Administration Officer"]:::perth
  n_callum_reid["Callum Reid<br/>Finance Manager"]:::perth
  n_priya_raman["Priya Raman<br/>Payroll Officer"]:::perth
  n_carol["Carol Singh<br/>Accounts Receivable Officer"]:::perth
  n_dave["Dave Okafor<br/>Accounts Payable Officer"]:::perth
  n_leila_haddad["Leila Haddad<br/>HR Adviser"]:::perth
  n_mei_chen["Mei Chen<br/>Recruitment and Training Coordinator"]:::perth
  n_jorge_alvarez["Jorge Alvarez<br/>Procurement Manager"]:::perth
  n_tamsin_clarke["Tamsin Clarke<br/>Procurement Officer"]:::perth
  n_raj_patel["Raj Patel<br/>Buyer"]:::perth
  n_olivia_brandt["Olivia Brandt<br/>Business Development Manager"]:::perth
  n_samuel_adeyemi["Samuel Adeyemi<br/>Contracts Administrator"]:::perth
  n_chloe_dubois["Chloe Dubois<br/>Bid and Tender Coordinator"]:::perth
  n_dana_whitlock["Dana Whitlock<br/>Operations Manager"]:::perth
  n_bob["Bob Tran<br/>Fleet Service Planner"]:::perth
  n_ethan_park["Ethan Park<br/>Shutdown Coordinator"]:::perth
  n_isla_mcgregor["Isla McGregor<br/>Rostering Coordinator"]:::perth
  n_fatima_ali["Fatima Ali<br/>Rostering Officer"]:::perth
  n_liam_oconnor["Liam O'Connor<br/>Logistics and Dispatch Coordinator"]:::perth
  n_zoe_kowalski["Zoe Kowalski<br/>Customer Service Coordinator"]:::perth
  n_kieran_doyle["Kieran Doyle<br/>Customer Service Officer"]:::perth
  n_anika_sharma["Anika Sharma<br/>Operations Administrator"]:::perth
  n_marcus_lee["Marcus Lee<br/>Fabrication Coordinator"]:::perth
  n_helen_cartwright["Helen Cartwright<br/>Safety and Quality Manager"]:::perth
  n_dmitri_volkov["Dmitri Volkov<br/>Safety Adviser"]:::perth
  n_ben_fitzgerald["Ben Fitzgerald<br/>Planning and Engineering Manager"]:::perth
  n_grace_tanaka["Grace Tanaka<br/>Senior Planner"]:::perth
  n_owen_hughes["Owen Hughes<br/>Maintenance Planner"]:::perth
  n_priscilla_ndlovu["Priscilla Ndlovu<br/>Maintenance Planner"]:::perth
  n_yusuf_khan["Yusuf Khan<br/>Mechanical Engineer"]:::perth
  n_hannah_berg["Hannah Berg<br/>Structural Engineer"]:::perth
  n_vikram_nair["Vikram Nair<br/>Reliability Engineer"]:::perth
  n_ruby_sullivan["Ruby Sullivan<br/>Senior Drafter"]:::perth
  n_callan_wright["Callan Wright<br/>Drafter"]:::perth
  n_anh_pham["Anh Pham<br/>Estimator"]:::perth
  n_jasmine_cole["Jasmine Cole<br/>Document Controller"]:::perth
  n_noah_bennett["Noah Bennett<br/>Apprentice Draftsperson"]:::perth
  n_mia_fernandez["Mia Fernandez<br/>Graduate Engineer"]:::perth
  n_ravi_kapoor["Ravi Kapoor<br/>Systems and Network Administrator"]:::perth
  n_erin["Erin Walsh<br/>IT Support Officer"]:::perth
  n_tom_nguyen["Tom Nguyen<br/>Site Supervisor (day shift)"]:::site
  n_shane_kelly["Shane Kelly<br/>Site Supervisor (night shift)"]:::site
  n_nikki_ward["Nikki Ward<br/>Site Safety Officer"]:::site
  n_trent_jackson["Trent Jackson<br/>Site Planner (days)"]:::site
  n_lucia_moretti["Lucia Moretti<br/>Site Planner (nights)"]:::site
  n_jarrah_cooper["Jarrah Cooper<br/>Site Administration and Timesheets Clerk"]:::site
  n_wendy_holloway["Wendy Holloway<br/>Storeperson"]:::site
  n_darren_pike["Darren Pike<br/>Leading Hand (Fleet Servicing)"]:::site
  n_sione_tuilagi["Sione Tuilagi<br/>Leading Hand (Fabrication)"]:::site
  n_billy_watson["Billy Watson<br/>Heavy Diesel Fitter"]:::site
  n_aroha_rangi["Aroha Rangi<br/>Heavy Diesel Fitter"]:::site
  n_jack_ferris["Jack Ferris<br/>Fitter"]:::site
  n_lachlan_dwyer["Lachlan Dwyer<br/>Apprentice Fitter"]:::site
  n_nathan_coker["Nathan Coker<br/>Boilermaker Welder"]:::site
  n_kelsey_murray["Kelsey Murray<br/>Boilermaker Welder"]:::site
  n_margaret_osei --> n_alice
  n_margaret_osei --> n_gail_sutherland
  n_gail_sutherland --> n_hamish_mcleod
  n_gail_sutherland --> n_sofia_rossi
  n_gail_sutherland --> n_tyler_barnes
  n_margaret_osei --> n_callum_reid
  n_callum_reid --> n_priya_raman
  n_callum_reid --> n_carol
  n_callum_reid --> n_dave
  n_margaret_osei --> n_leila_haddad
  n_leila_haddad --> n_mei_chen
  n_margaret_osei --> n_jorge_alvarez
  n_jorge_alvarez --> n_tamsin_clarke
  n_jorge_alvarez --> n_raj_patel
  n_margaret_osei --> n_olivia_brandt
  n_olivia_brandt --> n_samuel_adeyemi
  n_olivia_brandt --> n_chloe_dubois
  n_margaret_osei --> n_dana_whitlock
  n_dana_whitlock --> n_bob
  n_dana_whitlock --> n_ethan_park
  n_dana_whitlock --> n_isla_mcgregor
  n_isla_mcgregor --> n_fatima_ali
  n_dana_whitlock --> n_liam_oconnor
  n_dana_whitlock --> n_zoe_kowalski
  n_zoe_kowalski --> n_kieran_doyle
  n_dana_whitlock --> n_anika_sharma
  n_dana_whitlock --> n_marcus_lee
  n_margaret_osei --> n_helen_cartwright
  n_helen_cartwright --> n_dmitri_volkov
  n_margaret_osei --> n_ben_fitzgerald
  n_ben_fitzgerald --> n_grace_tanaka
  n_ben_fitzgerald --> n_owen_hughes
  n_ben_fitzgerald --> n_priscilla_ndlovu
  n_ben_fitzgerald --> n_yusuf_khan
  n_ben_fitzgerald --> n_hannah_berg
  n_ben_fitzgerald --> n_vikram_nair
  n_ben_fitzgerald --> n_ruby_sullivan
  n_ruby_sullivan --> n_callan_wright
  n_ben_fitzgerald --> n_anh_pham
  n_ben_fitzgerald --> n_jasmine_cole
  n_ruby_sullivan --> n_noah_bennett
  n_yusuf_khan --> n_mia_fernandez
  n_margaret_osei --> n_ravi_kapoor
  n_ravi_kapoor --> n_erin
  n_dana_whitlock --> n_tom_nguyen
  n_dana_whitlock --> n_shane_kelly
  n_tom_nguyen --> n_nikki_ward
  n_tom_nguyen --> n_trent_jackson
  n_shane_kelly --> n_lucia_moretti
  n_tom_nguyen --> n_jarrah_cooper
  n_tom_nguyen --> n_wendy_holloway
  n_tom_nguyen --> n_darren_pike
  n_shane_kelly --> n_sione_tuilagi
  n_darren_pike --> n_billy_watson
  n_darren_pike --> n_aroha_rangi
  n_darren_pike --> n_jack_ferris
  n_darren_pike --> n_lachlan_dwyer
  n_sione_tuilagi --> n_nathan_coker
  n_sione_tuilagi --> n_kelsey_murray
  classDef perth fill:#8547AD,stroke:#323E48,color:#fff
  classDef site fill:#E6D9EF,stroke:#323E48,color:#323E48
```

## The same chart as a list

- **Margaret Osei**, General Manager (Executive, Perth)
  - **Alice Nguyen**, Executive Assistant (Executive, Perth)
  - **Gail Sutherland**, Office Manager (Office Administration, Perth)
    - **Hamish McLeod**, Receptionist (Office Administration, Perth)
    - **Sofia Rossi**, Administration Officer (Office Administration, Perth)
    - **Tyler Barnes**, Trainee Administration Officer (Office Administration, Perth)
  - **Callum Reid**, Finance Manager (Finance and Payroll, Perth)
    - **Priya Raman**, Payroll Officer (Finance and Payroll, Perth)
    - **Carol Singh**, Accounts Receivable Officer (Finance and Payroll, Perth)
    - **Dave Okafor**, Accounts Payable Officer (Finance and Payroll, Perth)
  - **Leila Haddad**, HR Adviser (People and Culture, Perth)
    - **Mei Chen**, Recruitment and Training Coordinator (People and Culture, Perth)
  - **Jorge Alvarez**, Procurement Manager (Procurement, Perth)
    - **Tamsin Clarke**, Procurement Officer (Procurement, Perth)
    - **Raj Patel**, Buyer (Procurement, Perth)
  - **Olivia Brandt**, Business Development Manager (Business Development, Perth)
    - **Samuel Adeyemi**, Contracts Administrator (Business Development, Perth)
    - **Chloe Dubois**, Bid and Tender Coordinator (Business Development, Perth)
  - **Dana Whitlock**, Operations Manager (Operations, Perth)
    - **Bob Tran**, Fleet Service Planner (Operations, Perth)
    - **Ethan Park**, Shutdown Coordinator (Operations, Perth)
    - **Isla McGregor**, Rostering Coordinator (Operations, Perth)
      - **Fatima Ali**, Rostering Officer (Operations, Perth)
    - **Liam O'Connor**, Logistics and Dispatch Coordinator (Operations, Perth)
    - **Zoe Kowalski**, Customer Service Coordinator (Operations, Perth)
      - **Kieran Doyle**, Customer Service Officer (Operations, Perth)
    - **Anika Sharma**, Operations Administrator (Operations, Perth)
    - **Marcus Lee**, Fabrication Coordinator (Operations, Perth)
    - **Tom Nguyen**, Site Supervisor (day shift) (Site Operations, site)
      - **Nikki Ward**, Site Safety Officer (Safety and Quality, site)
      - **Trent Jackson**, Site Planner (days) (Site Operations, site)
      - **Jarrah Cooper**, Site Administration and Timesheets Clerk (Site Operations, site)
      - **Wendy Holloway**, Storeperson (Site Operations, site)
      - **Darren Pike**, Leading Hand (Fleet Servicing) (Fleet Servicing, site)
        - **Billy Watson**, Heavy Diesel Fitter (Fleet Servicing, site)
        - **Aroha Rangi**, Heavy Diesel Fitter (Fleet Servicing, site)
        - **Jack Ferris**, Fitter (Fleet Servicing, site)
        - **Lachlan Dwyer**, Apprentice Fitter (Fleet Servicing, site)
    - **Shane Kelly**, Site Supervisor (night shift) (Site Operations, site)
      - **Lucia Moretti**, Site Planner (nights) (Site Operations, site)
      - **Sione Tuilagi**, Leading Hand (Fabrication) (Fabrication, site)
        - **Nathan Coker**, Boilermaker Welder (Fabrication, site)
        - **Kelsey Murray**, Boilermaker Welder (Fabrication, site)
  - **Helen Cartwright**, Safety and Quality Manager (Safety and Quality, Perth)
    - **Dmitri Volkov**, Safety Adviser (Safety and Quality, Perth)
  - **Ben Fitzgerald**, Planning and Engineering Manager (Planning and Engineering, Perth)
    - **Grace Tanaka**, Senior Planner (Planning and Engineering, Perth)
    - **Owen Hughes**, Maintenance Planner (Planning and Engineering, Perth)
    - **Priscilla Ndlovu**, Maintenance Planner (Planning and Engineering, Perth)
    - **Yusuf Khan**, Mechanical Engineer (Planning and Engineering, Perth)
      - **Mia Fernandez**, Graduate Engineer (Planning and Engineering, Perth)
    - **Hannah Berg**, Structural Engineer (Planning and Engineering, Perth)
    - **Vikram Nair**, Reliability Engineer (Planning and Engineering, Perth)
    - **Ruby Sullivan**, Senior Drafter (Planning and Engineering, Perth)
      - **Callan Wright**, Drafter (Planning and Engineering, Perth)
      - **Noah Bennett**, Apprentice Draftsperson (Planning and Engineering, Perth)
    - **Anh Pham**, Estimator (Planning and Engineering, Perth)
    - **Jasmine Cole**, Document Controller (Planning and Engineering, Perth)
  - **Ravi Kapoor**, Systems and Network Administrator (Information Technology, Perth)
    - **Erin Walsh**, IT Support Officer (Information Technology, Perth)

## Shared mailboxes

| Mailbox             | Name             | Responsible person                             |
| ------------------- | ---------------- | ---------------------------------------------- |
| `info@boab.lab`     | Company Info     | Gail Sutherland, Office Manager                |
| `sales@boab.lab`    | Sales Enquiries  | Olivia Brandt, Business Development Manager    |
| `accounts@boab.lab` | Accounts Team    | Callum Reid, Finance Manager                   |
| `service@boab.lab`  | Customer Service | Zoe Kowalski, Customer Service Coordinator     |
| `security@boab.lab` | IT Security      | Ravi Kapoor, Systems and Network Administrator |
| `hr@boab.lab`       | Human Resources  | Leila Haddad, HR Adviser                       |

Staff who answer a shared mailbox sign in to its account (see `docs/build/12-mail.md`).
