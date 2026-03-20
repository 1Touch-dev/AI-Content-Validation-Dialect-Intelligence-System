# Honduras Dataset Bias Audit

## 1. Source Analysis
- **Total Records**: 5000
- **Real Records**: 1633 (32.7%)
- **Synthetic Records**: 3367 (67.3%)

## 2. Language Pattern Analysis (Slang Frequency)
- **maje**: Overall 13.0% | Real 0.2% | Synthetic 19.2%
- **pijudo**: Overall 1.0% | Real 0.0% | Synthetic 1.5%
- **cipote**: Overall 3.1% | Real 0.0% | Synthetic 4.5%
- **vos**: Overall 1.1% | Real 0.2% | Synthetic 1.5%

## 3. Style Distribution
- **Average Sentence Length**:
  - Real: 38.4 words
  - Synthetic: 41.4 words
- **Vocabulary Diversity (Unique/Total Words)**:
  - Real: 0.1693
  - Synthetic: 0.0835

## 4. Duplicate Pattern Check
- Pairs with > 0.90 similarity (estimated/counted): 400

## 5. Flags & Risks
⚠️ Synthetic records exceed 60% (67.3%). High risk of model over-fitting to synthetic generation patterns.
⚠️ High number of extremely similar records estimated (400 pairs > 0.90 sim). Risk of duplicates.

## 6. Real-World Validation Sample (20 Random Real Samples)
1. *Este nuevo concepto visual y musical es el preludio de su esperado regreso a Honduras, donde se presentará el próximo sábado 18 de abril de 2026 en el Palacio Universitario de los Deportes UNAH de Tegucigalpa. https://t.co/e9deCWhV6z*
2. *Oferta de Empleo: Abogado/a Consultor/Asesor en Compliance (San Pedro Sula - Cort?s (Honduras)) https://t.co/rgDZecGoDA https://t.co/u17vvSMQ9B*
3. *🟡| ¿Será deportada? Una historia que estuvo marcada por años de espera. La justicia revisó el caso de una hondureña que pasó 22 años en prisión en EE. UU. y su situación dio un nuevo rumbo ⚖️🏛️. Los detalles aquí 👉🏻: https://t.co/2x19qI1dB0 #Honduras #EstadosUnidos #Justicia #Migración*
4. *¿Por qué la venta directa🤝🏻 gana espacio en la nueva era de compra💵? #VoxPopuliHN #Honduras https://t.co/Zo6Th71YEG*
5. *🥹 Otro joven motociclista falleció en las calles de San Pedro Sula. Esta mañana, Axel Fabián Peña Méndez perdió la vida tras chocar con una rastra. Familia pide prudencia vial 🚛🕊️. Conoce los detalles aquí 👉🏻: https://t.co/fpQjp80Tfj #Conductor #Rastra #Accidente #Honduras https://t.co/YMpF2oJgzb*
6. *@Lorenhn_ @SARHonduras Aunque el lugar parece que es La casca de san pedro sula.*
7. *#Internacional | Una mujer de 78 años murió en Tegucigalpa por miasis causada por el gusano barrenador. Honduras registra 76 casos humanos en 2026. 👉 Más detalles en la nota: https://t.co/oOdaIQXbHt*
8. *¡FUE PARTE DEL MONSTRUO EN 2006!🥺 El exguardameta que defendió la portería del Marathón y que también tuvo paso por el fútbol europeo falleció este martes.🕊️ La causa de su fallecimiento 👉🏻 https://t.co/E7VvJ6BEsd #Marathón #LigaNacional #Honduras #MauricioNanni https://t.co/vssivOaQLk*
9. *Exministro Cardona señala a Luis Redondo🧔🏻‍♂️ por origen del fondo “Chequesol” y pide que declare ante juez👨🏻‍⚖️ #VoxPopuliHN #Honduras https://t.co/ZTNZOglvCp*
10. *Hotel Clarión Tegucigalpa muestra nuevas tendencias para eventos corporativos y sociales en su Open House de Banquetes 2026 https://t.co/TZpLgmaFjN*
11. *EEUU🇺🇸 afirma haber destruido "casi toda" la capacidad nuclear de Irán🇮🇷 #VoxPopuliHN #Honduras https://t.co/KMc71huZo1*
12. *La mansión del cuñado de ‘El Mencho’ en Punta del Este fue subastada en USD 1,200,000🤯 #VoxPopuliHN #Honduras https://t.co/FWwGsr1lv5*
13. *@PesteRana Con razón los de Cerrocigalpa sienten que estan en Estados Unidos cuando llegan a San Pedro Sula, que vaina mas horrible esa.*
14. *Ministra de DD. HH. denuncia pagos de hasta L300,000 mensuales💵 a familia en sistema de protección😳; Angélica Álvarez lo niega #VoxPopuliHN #Honduras https://t.co/ecGpTnkdpD*
15. *#EPActualidad | El titular del Poder Legislativo, Tomás Zambrano, entregó este sábado al Hogar Hermanas de Jesús Buen Samaritano, en San Pedro Sula, el decreto aprobado el mes pasado; que exonera a esta institución del pago del servicio de energía eléctrica. #ElPulso https://t.co/UxakoNUpmm*
16. *Fortalecen la logística en Honduras con apoyo del PNUD. ¡Un futuro más verde! 🌱 https://t.co/oRdU6ft4XO*
17. *❌Godofredo Fajardo propone suprimir TJE y UFTF para ahorrar L400 millones #ForumNews #ForumEncuestas #Honduras https://t.co/2Ol3M0Gyqh*
18. *#Internacionales || #Honduras confirmó el primer fallecimiento por miasis causada por el gusano barrenador en lo que va del año. El jefe de la Unidad de Vigilancia de la Salud, Hommer Mejía, indicó que la víctima es una mujer de 78 años, originaria de Tegucigalpa. https://t.co/Rv7giY9weR*
19. *https://t.co/pFCzHVkm9J Autoridades de la Universidad Nacional Autónoma de Honduras (UNAH), realizaron una radiografía sobre la gestión del nuevo gobierno a casi 40 días de haber tomado la administración nacional. Lee la nota completa.*
20. *Es un lugar muy bonito me encanta su tranquilidad y la amabilidad son muy atentos lo he visitado como tres veces pero con años de diferencia porque no es mi fuerte pero la veces que he ido ha Sido un 50 /50 la verdad no me gusta la comida en absoluto bueno el desayuno la última vez 15/3/25 me pedí una baleada y mi hijo unos panqueque la baleada horrible aquello utilizan demaciada soda en la harina y no queda suave ni nada los panqueque de mi hijo olían demasiado a huevo y sabía horrible aquello;mi hijo se lo comió porque lo obligue y pedí una granitas de café fue lo peor y yo que tenía un antojo de granizado hace tiempos pero la granita de este lugar me hizo no volver a pensar en ello ; la verdad la comida es muy mala allí aparte del precio arriba de los 170 ; 180 ; iré a pedir trabajo allí para que vean la diferencia de comida y como se cocina😊😊*

## 7. Final Recommendation
**Dataset requires additional real data scraping or careful downsampling of synthetic records.** Synthetic distribution and/or single-token bias is too high, leading to likely model brittle behavior in real-world inference.