# 🇰🇪 The Official 125 Rules Specification of Loosely Swahili
> **Comprehensive Morphosyntactic, Phonotactic, and Sociolinguistic Rule Engine for East African Kenyan Code-Switching & Sheng**  
> *Package:* `loosely-swahili` (v0.3.0) | *Author:* Maxwell Ng'ang'a ([@Eminek-marz](https://github.com/Eminek-marz))

---

## Executive Architectural Summary

Standard Natural Language Processing models fail catastrophically across East Africa because they presuppose a hard binary: either 100% formal Queen's English or 100% textbook Kiswahili Sanifu. In genuine spoken and written communication across Kenya, speakers employ **Loosely Swahili**—a highly evolved, rule-governed contact language that fuses **Bantu structural hardware** (concord chains, agglutinative prefixes, infixes, and phonotactic harmony) with **English and Sheng lexical software** (uninflected roots optimized for high-velocity syllable economy).

This specification codifies the complete **125 Rules of Loosely Swahili**, organized into 7 linguistic categories:
1. **Category I: Morphosyntactic Verbal Agglutination & Affixation** (Rules 1 – 25)
2. **Category II: Nominal Classes, Pluralization & Concord** (Rules 26 – 45)
3. **Category III: Deixis, Demonstratives & Modifiers** (Rules 46 – 65)
4. **Category IV: Syntax, Locatives & Prepositions** (Rules 66 – 85)
5. **Category V: Phonology, Metathesis & Epenthesis** (Rules 86 – 100)
6. **Category VI: Digital, Financial & M-Pesa Pragmatics** (Rules 101 – 115)
7. **Category VII: Discourse Anchors, Modals & Sociolinguistics** (Rules 116 – 125)

---

## 📌 Category I: Morphosyntactic Verbal Agglutination & Affixation (Rules 1 – 25)

1. **Rule 1: The Bare Root Invariant** – English verb roots must remain in their uninflected base form (e.g., `alikuwa amepick`, rejecting `*amepicked`; `nimeshock`, rejecting `*nimeshocked`).
2. **Rule 2: Subject-Tense-Object Verbal Plug-In** – Canonical Swahili prefix order attached to the bare English root: `[Subj] + [Tense] + [Obj] + [BareRoot]` (`ali-tu-call`, `wame-m-block`).
3. **Rule 3: Mid-Sentence Negative Infixation** – Present tense negative prefix attached directly to bare root (`si-care`, `hatu-match`, `hawa-care`).
4. **Rule 4: Past Negation (`-ku-`)** – Absolute past negation with bare root (`si-ku-call`, `hau-ku-reply`).
5. **Rule 5: "Not Yet" Aspectual Negation (`-ja-`)** – Incomplete aspect negation (`si-ja-clean`, `hatu-ja-deploy`).
6. **Rule 6: Habitual Consecutive Prefix (`hu-`)** – Habitual actions taking uninflected loan root (`hu-stream`, `hu-code`).
7. **Rule 7: Epenthetic `i` in Passive Extensions (*Kutendwa*)** – English silent `-e` drops with epenthetic `i` before `-wa` (`fire` $\rightarrow$ `alifiriwa`, `promote` $\rightarrow$ `alipromotiwa`).
8. **Rule 8: Epenthetic `i` in Stative Extensions (*Kutendeka*)** – English root takes epenthetic `i` before `-ka` (`solve` $\rightarrow$ `ina-solvika`, `hack` $\rightarrow$ `ina-hackika`).
9. **Rule 9: Euphonic `r` Epenthesis for Open-Vowel Stems** – Epenthetic `r` prevents hiatus before passive/applicative (`share` $\rightarrow$ `tuta-shareriwa`).
10. **Rule 10: Periphrastic Reciprocal (`pamoja` Rule)** – Bare English root pairs with `pamoja` instead of illegal synthetic reciprocal suffix (e.g., `tunavibe pamoja`, never `*tunavibeana`).
11. **Rule 11: Applicative Benefactive Extension (*Kutendea*)** – Syllable-conditioned `-ia` / `-ea` attached to loan roots (`book` $\rightarrow$ `ani-bookie`, `order` $\rightarrow$ `tu-orderie`).
12. **Rule 12: Causative Extension (*Kutendesha*)** – Loan roots taking `-isha` / `-esha` (`sign` $\rightarrow$ `a-signishe`, `stop` $\rightarrow$ `a-stopishe`).
13. **Rule 13: Stative-Potentive Modality (*Kutendana/Kutendeka*)** – Feasibility modality (`manage` $\rightarrow$ `ina-manage-ka`).
14. **Rule 14: Reflexive Infix (`-ji-`)** – Transitive English verbs taking Bantu reflexive marker (`ana-ji-promote`, `wali-ji-expose`).
15. **Rule 15: Negative Gerund Prefixation (`bila ku-`)** – Negative gerund constructions (`bila ku-notice`, `bila ku-hesitate`).
16. **Rule 16: Negative Gerund Object Infixing (`bila ku-[obj]-root`)** – Transitive gerund negation with object concord (`bila wewe ku-wa-notice`).
17. **Rule 17: Conditional Infix (`-ki-`)** – Realis conditional clauses (`uki-arrive`, `waki-delay`).
18. **Rule 18: Hypothetical Subjunctive Infix (`-nge-`)** – Potential conditional mood (`ange-accept`, `tunge-win`).
19. **Rule 19: Past Counterfactual Infix (`-ngali-`)** – Unfulfilled past conditional (`angali-show up`, `tangali-fail`).
20. **Rule 20: Perfective State Infix (`-me-`)** – Completed action with enduring present state (`ame-shock`, `zime-hang`).
21. **Rule 21: Progressive Aspect Infix (`-na-`)** – Continuous ongoing action (`ana-type`, `ina-load`).
22. **Rule 22: Remote Past Infix (`-ali-`)** – Distant past marker (`wali-relocate kitambo`).
23. **Rule 23: Immediate Future Infix (`-ta-`)** – Prospective future marker (`tuta-chat badae`).
24. **Rule 24: Iterative Infix (`-ka-`)** – Narrative sequential consecutive marker (`aka-click, aka-login`).
25. **Rule 25: Relative Infix Incorporation (`-ye-`, `-o-`, `-cho-`)** – Subject/object relative pronouns embedded into the verb head (`msee a-ye-login`, `file i-yo-corrupt`).

---

## 📌 Category II: Nominal Classes, Pluralization & Concord (Rules 26 – 45)

26. **Rule 26: Binary Noun Class Collapse (A-WA vs I-ZI)** – Simplification of 18 traditional Bantu noun classes into 2 operational streams: Animate/Human (A-WA) and Inanimate/Abstract/Systemic (I-ZI).
27. **Rule 27: The English "-s" Double-Stack Plural** – Prefixing collective `Ma-` while preserving English plural `-s` (`maphones`, `maservers`, `mabooks`).
28. **Rule 28: Food Plural Economy Constraint** – Exclusion of collective `Ma-` from imported foods/pastries (`chapos`, never `*machapo`).
29. **Rule 29: Loan Word Plural Concord Agreement** – Imported plural nouns in I-ZI triggering `zi-` subject agreement (`maservers zime-crash`).
30. **Rule 30: Human Plural Concord Agreement** – Imported human roles triggering `wa-` subject agreement (`mabosses wame-agree`).
31. **Rule 31: Zero-Derivation Mass Nouns** – Uncountable English mass nouns treated as singular I-ZI (`software ime-update`, `code iko clean`).
32. **Rule 32: Class 7/8 Diminutive Loan Prefixation (`Ki-` / `Vi-`)** – Diminutive formation on loan stems (`kikazi`, `vikazi`).
33. **Rule 33: Class 5 Augmentative Formation (`Ji-` / Zero)** – Augmentative size/magnitude shifts (`jiboss`, `jijam`).
34. **Rule 34: Compound Loan Nouns** – Head-first Bantu syntax governing English multi-word noun clusters (`market ya nje`, `system ya malipo`).
35. **Rule 35: Acronym Inanimate Classification** – Tech and institutional acronyms defaulting to I-ZI singular/plural (`API ime-fail`, `hizi SDKs ziko fast`).
36. **Rule 36: Double Plural Deletion Avoidance** – Ban on removing English stem `-s` when suffix is integral (`boss` $\rightarrow$ `maboss`, not `*mabo`).
37. **Rule 37: Kinship and Peer Grouping (`Kin-ma`)** – Group collective marker on familial/peer heads (`kina John`, `kina bro`).
38. **Rule 38: Abstract Quality Nominalization (`U-` Prefix)** – Forming abstract nouns from English adjectives/nouns (`u-celebrity`, `u-expert`).
39. **Rule 39: Agentive Nominalization (`M-` / `Wa-` Prefix)** – Deriving animate professions (`m-developer`, `wa-developer`).
40. **Rule 40: Borrowed Proper Noun Locative Non-inflection** – Exclusion of `-ni` suffix from foreign named entities (`Nairobi`, `Google`, never `*Googleni`).
41. **Rule 41: Native Common Noun Locative Attachment** – Enforcing `-ni` for indigenous common locatives (`mtaani`, `chumbani`).
42. **Rule 42: Animate Non-Locative Constraint** – Ban on attaching locative `-ni` to living persons (`kwa daktari`, never `*daktarini`).
43. **Rule 43: Adjectival Concord Agreement in Living Classes** – Human adjectives taking `m-` / `wa-` (`msee m-clever`, `wasee wa-smart`).
44. **Rule 44: Adjectival Concord Agreement in Object Classes** – Object adjectives taking `i-` / `zi-` (`simu i-cheap`, `simu zi-expensive`).
45. **Rule 45: Invariable Loan Adjectives** – High-velocity English color/status adjectives remaining uninflected (`gari blue`, `t-shirt fresh`).

---

## 📌 Category III: Deixis, Demonstratives & Modifiers (Rules 46 – 65)

46. **Rule 46: Proximal Demonstrative Selection (`Hii` / `Hizi`)** – Immediate deictic proximity for objects (`hii bug`, `hizi errors`).
47. **Rule 47: Distal Demonstrative Compression (`Iyo` / `Izo`)** – Phonetically reduced distal demonstratives (`iyo deal`, `izo files`).
48. **Rule 48: Remote Distal Demonstrative (`Ile` / `Zile`)** – Spatial/temporal remoteness (`ile project ya juzi`).
49. **Rule 49: Large Object Deictic Shift (`Hili` / `Haya`)** – Physical complexes/buildings selecting Class 5 demonstrative (`hili complex`, `haya majengo`).
50. **Rule 50: Demonstrative Fronting for Topicalization** – Placing demonstratives before the noun phrase for emphasis (`hizi issues lazima zi-fix-iwe`).
51. **Rule 51: Demonstrative Post-Positioning for Definiteness** – Placing demonstrative after noun to indicate given information (`issue hii ni ngumu`).
52. **Rule 52: Manner Adverbs via `Ki-` Prefix** – Converting loan adjectives to adverbs of manner (`ki-pro`, `ki-amateur`).
53. **Rule 53: Manner Adverbs via `Vi-` Prefix** – Intensive adverbial manner formation (`vi-badly`, `vi-stupid`).
54. **Rule 54: Post-Nominal Possessive Concord (I-ZI)** – Possessive pronouns following the noun (`laptop yangu`, `laptops zangu`).
55. **Rule 55: Post-Nominal Possessive Concord (A-WA)** – Possessive pronouns following human heads (`colleague wangu`, `colleagues wangu`).
56. **Rule 56: Pre-Nominal English Possessive Borrowing** – Importing English possessive pronouns pre-nominally with Bantu boundary verb concord (`my code ina-run`, `your meeting ime-start`).
57. **Rule 57: Universal Quantifier Distribution (`Kila`)** – Invariable distributive quantifier preceding noun (`kila commit`, `kila department`).
58. **Rule 58: Totalizing Quantifier Concord (`-ote`)** – Inflected totalizer following head noun (`team yote`, `servers zote`).
59. **Rule 59: Selective Partitive Quantifier (`-ingine`)** – Indefinite/alternative selector (`plan nyingine`, `msee mwingine`).
60. **Rule 60: Post-Verbal Adverbial Intensifier (`Sana`)** – Frequency and magnitude modifier (`ina-lag sana`, `ina-speed sana`).
61. **Rule 61: Reduplicative Intensification** – Doubling adjectives/adverbs for hyperbolic emphasis (`haraka haraka`, `fiti fiti`).
62. **Rule 62: Superlative Construction via Verb `Shinda` / `Zidi`** – Expressing extremes through comparative victory verbs (`hii ndio ina-perform kushinda zote`).
63. **Rule 63: Approximative Quantity Modification (`Kama`)** – Approximations before numerical quantities (`kama thao mbili`, `kama 10 minutes`).
64. **Rule 64: Diminutive Quantity Modification (`Kidogo`)** – Softening requests and assertions (`reduce bei kidogo`, `hold on kidogo`).
65. **Rule 65: Extreme Quantity Slang Intensifier (`Mob`)** – Indefinite massive quantity marker (`tuko na work mob`, `kuna errors mob`).

---

## 📌 Category IV: Syntax, Locatives & Prepositions (Rules 66 – 85)

66. **Rule 66: The Zero-Preposition Locative** – Omission of prepositions before routine destinations (`niko job`, `enda town`, `tuko home`).
67. **Rule 67: The Universal Locative Overlord (`Kwa`)** – Generalized preposition for non-routine entities and digital loci (`kwa database`, `kwa group`, `kwa server`).
68. **Rule 68: Human Target Locative (`Kwa`)** – Compulsory `kwa` when navigating to persons (`tuna-enda kwa msee wa IT`).
69. **Rule 69: Temporal Punctuality Boundary (`By`)** – Importing English temporal preposition `by` for deadlines (`finish by jioni`, `deploy by saa nne`).
70. **Rule 70: Causal Connector Fronting (`Coz` / `Kwa Sababu`)** – Reason clauses introduced without morphological shifts (`coz API ili-timeout`).
71. **Rule 71: Adversative Concession (`Hata Kama`)** – Subordinate clause marker preserved before hybrid matrix (`hata kama server ime-load`).
72. **Rule 72: Conditional Marker (`Kama`)** – Protasis clause marker for conditional sentences (`kama mteja ata-cancel`).
73. **Rule 73: Contrastive Topic Marker (`Lakini` / `But`)** – Coordination boundary preserving separate linguistic codes (`tume-test, lakini bado ina-fail`).
74. **Rule 74: Resultative Consequence (`So` / `Basi`)** – Illative connector bridging cause and effect (`link ili-expire, so ikabidi ni-resend`).
75. **Rule 75: Focus Clef Marker (`Ndio`)** – Cleft focus particle highlighting subjects or instruments (`huyu dev ndio ali-merge code`).
76. **Rule 76: WH-Interrogative Fronting with Focus (`Nani`)** – Interrogative subject fronted with verbal concord (`nani ata-approve PR?`).
77. **Rule 77: WH-Interrogative In-Situ Placement (`Wapi`)** – Locative question particle retained sentence-finally (`ume-save hii file wapi?`).
78. **Rule 78: Interrogative Reason Suffixation (`Kwa Nini` / `Mbona`)** – Pre-verbal cause questions (`mbona unani-ignore?`).
79. **Rule 79: Manner Question Particle (`Aje`)** – Post-verbal question for execution mechanisms (`hii script ina-run aje?`).
80. **Rule 80: Instrumental Preposition (`Na`)** – Linking tools, technologies, and agents (`tuna-build na React`, `ili-andikwa na intern`).
81. **Rule 81: Comitative Associative Particle (`Na`)** – Expressing accompaniment with coordinate concord (`niko na team yangu`).
82. **Rule 82: Comparative Simile Particle (`Kama`)** – Equational comparisons across noun phrases (`ina-run fast kama C++`).
83. **Rule 83: Directional Source Locative (`Kutoka`)** – Ablative spatial movement (`tume-pull data kutoka AWS`).
84. **Rule 84: Directional Target Locative (`Hadi` / `Mpaka`)** – Allative terminative boundary (`tuta-code mpaka asubuhi`).
85. **Rule 85: Inclusive Universal Particle (`Pamoja Na`)** – Additive association encompassing supplementary items (`backend pamoja na frontend`).

---

## 📌 Category V: Phonology, Metathesis & Epenthesis (Rules 86 – 100)

86. **Rule 86: Syllabic Open-Vowel Constraint (Bantu CV Structure)** – Insertion of final vowel to closed English consonants (`look` $\rightarrow$ `luku`, `book` $\rightarrow$ `buku`).
87. **Rule 87: Syllable Onset Liquid Glide Assimilation (`L` $\leftrightarrow$ `R`)** – Free phonetic variation in loan roots (`calculate` $\rightarrow$ `kukalkyuleti`).
88. **Rule 88: Cluster Simplification via Epenthetic Vowels** – Breaking consonant clusters to maintain moraic rhythm (`screen` $\rightarrow$ `sikirini`).
89. **Rule 89: Metathesis Syllable Reversal (2-Syllable Inversion)** – Syllable swapping in youth slang (`dawa` $\rightarrow$ `wada`, `pesa` $\rightarrow$ `sape`).
90. **Rule 90: Metathesis Consonant Shift (Inverted Stems)** – Phonetic inversion of root consonants (`chwani` $\rightarrow$ `ngao`, `sister` $\rightarrow$ `sista` $\rightarrow$ `mbeshte`).
91. **Rule 91: Vowel Elision in High-Velocity Speech** – Dropping unaccented vowels at word boundaries (`wewe uko` $\rightarrow$ `we uko`, `yeye ako` $\rightarrow$ `ye ako`).
92. **Rule 92: Nasal Prefix Homorganicity** – Nasal assimilation before bilabial and velar consonants (`m-` before `p/b`, `n-` before `t/d`).
93. **Rule 93: Devoicing of Loan Final Obstruents** – Tending toward voiceless stops in word-final positions.
94. **Rule 94: Monophthongization of English Diphthongs** – Reducing complex diphthongs to pure vowels (`make` /eɪ/ $\rightarrow$ `meki` /e/).
95. **Rule 95: Vowel Lengthening for Emphatic Stress** – Penultimate syllable elongation for emotive signaling (`ile issue ilikuwa nguuumu!`).
96. **Rule 96: Tonal Accent Neutralization** – Mapping English lexical stress into Bantu penultimate stress rules.
97. **Rule 97: Sibilant Harmony in Slang Derivatives** – Harmonizing alveolar and palato-alveolar fricatives (`chapaa`, `chwani`).
98. **Rule 98: High Vowel Fronting before Palatal Approximants** – Pre-glide vocalic shifts in compound slangs.
99. **Rule 99: Intervocalic Fricative Weakening** – Softening stops between vowels in fast colloquial flow.
100. **Rule 100: Epenthetic Glottal Stop Elimination** – Smooth liaison across vowel-initial loan verbs (`u-load`, `a-update`).

---

## 📌 Category VI: Digital, Financial & M-Pesa Pragmatics (Rules 101 – 115)

101. **Rule 101: Transactional Command Bare Root (`Tuma`)** – Imperative mobile money transfer syntax (`tuma kwa hii number`).
102. **Rule 102: Reversal Particle Syntax (`Reverse`)** – Mobile money reversal action (`nime-request Safaricom wa-reverse`).
103. **Rule 103: Transaction Fulfilled Stative (`Ime-ingia`)** – Confirmation of incoming liquidity (`chapaa ime-ingia`).
104. **Rule 104: Transaction Exhausted Stative (`Ime-kata`)** – Fee deduction and balance drop (`Fuliza ime-kata fee yote`).
105. **Rule 105: Loan Application Root (`Fuliza` / `Kopa`)** – Overdraft facility syntax (`inabidi ni-fulize fare`).
106. **Rule 106: Currency Slang Value Anchoring (`Thao`)** – Thousands multiplier currency register (`thao tano` = KES 5,000).
107. **Rule 107: Currency Slang Fraction Anchoring (`So` / `Joo`)** – Hundreds multiplier currency register (`soo tano` = KES 500).
108. **Rule 108: Denomination Identity Mapping (`Chwani` / `Finje`)** – Fifty-shilling unit syntax (`finje`, `chwani`).
109. **Rule 109: Digital Verification Code Invariant (`OTP`)** – Zero-translation security credential noun (`tuma OTP mara moja`).
110. **Rule 110: Telecommunication Balance Query (`Kucheki Balance`)** – USSD query pragmatics (`cheki balance kwanza`).
111. **Rule 111: Network Congestion Metaphor (`Net Iko Down`)** – Telemetry connectivity failure state (`network ime-hang`, `net iko down`).
112. **Rule 112: Battery and Energy Depletion (`Ime-die`)** – Device power exhaustion (`simu yangu ime-die`).
113. **Rule 113: Airtime Scratch-Card Recharge (`Ku-load Bundles`)** – Data package acquisition syntax (`na-load data bundles`).
114. **Rule 114: Hardware Malfunction Metaphor (`Ku-choma`)** – Permanent component ruin or blown fuses (`hard drive ili-choma`).
115. **Rule 115: Screen Display Fracture (`Ku-crush Display`)** – Physical screen damage pragmatics (`display ili-crack`).

---

## 📌 Category VII: Discourse Anchors, Modals & Sociolinguistics (Rules 116 – 125)

116. **Rule 116: Sentence-Final Pragmatic Anchor (`Bana`)** – Conversational reality assertion marker (`haina noma bana`).
117. **Rule 117: Sentence-Initial Evidential Anchor (`Enyewe`)** – Conceding truth and factual reality (`enyewe hiyo bug ilikuwa tricky`).
118. **Rule 118: Sentence-Initial Distress Interjection (`Manze`)** – Emotional surprise or indignation (`manze nime-lose uncommitted changes`).
119. **Rule 119: Rhetorical Disbelief Tag (`Kwani`)** – Challenging baseline assumptions (`kwani hauku-pull latest changes?`).
120. **Rule 120: Solidarity Confirmation Particle (`Sindio` / `Si Eeh`)** – Seeking consensus at clause boundaries (`tutamaliza hii sprint leo, sindio?`).
121. **Rule 121: Deontic Necessity Modal (`Inabidi` / `Lazima`)** – Compulsory systemic requirement (`inabidi tu-refactor hii architecture`).
122. **Rule 122: Preferential Subjunctive Modal (`Afadhali`)** – Optimal path recommendation (`afadhali tu-tumie PostgreSQL`).
123. **Rule 123: Impossibility Stative Modal (`Haiwezi`)** – Asserting functional blockage (`hii query haiwezi fanya kazi bila index`).
124. **Rule 124: Reassurance Palliative Particle (`Haina Noma` / `Chill Tu`)** – De-escalating technical anxiety (`relax, haina noma, tuta-patch`).
125. **Rule 125: Code-Switching Boundary Invariant (The Poplack-Bantu Filter)** – Strict prohibition against switching languages across bound grammatical infixes or within monosyllabic prefixes (preserving syntactic integrity across all East African code-switching).
