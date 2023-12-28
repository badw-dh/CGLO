import difflib 
import os
import sys
import textwrap
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Project imports
from tag_CGL_xrefs import *

outfile = 'data/xref_test.txt'

TEST_PARS = [
r"""**Agnina** ἄρνειον κρέας II 245, 30. ἀρνεία III 316, 53; 364, 29; 400,
50; 489, 43; 509, 9. ἄρνειον III 16, 6; 88, 29; 364, 2; 398, 3.
**agminum** ἄρνειον III 187, 40; 255, 63.""",

r"""**Aeneator** σαλπικτής II 12, 3. tubarum factor II 565, 22 (*ubi* cantor
*Hildebrand p.* 5. *male versum*). **aenatores** κυμβαλοκροῦσται II
12, 4. **aeneatores** tubicines IV 11, 47; 12, 3; 204, 13; V 163, 48;
262, 48; 266, 47; 338, 42. **aenatores** cornicines IV 12, 11.
**aeneatores** cornic\<in\>es, liticines, tubicines IV 475, 33.
corni\<cin\>es, liticines V 262, 33. cornicines, liticines, id est corno
(cornu *de*) uel calamo canentes IV 306, 1; V 437, 46 (cornu). corno
(cornu *ab*) uel calamo cantantes IV 204, 18. *Cf. Festus Pauli* 20, 7.""",

r"""**Absonus** sine sono homo V 343, 31; 259, 46. **absonum** ἀπηχές II
235, 7. ἀνάρμοστον II 5, 21; 554, 58. ἀπηχές, ἀμαυρόν II 555, 2 (*v.*
absurdus). sine sono II 563, 39 (= *Non.* 72, 5). **absono** non simili
sono IV 5, 19; 202, 3. praepostero, absurdo *cod. Leid.* 67 *E*
(*Prodr.* 148). absurdo uel praepostero *a post* IV 4, 44 (propero
*cod.*); IV 4, 44 (propero *cod.: om. bc*).""",

r"""**Abdomen** λαπάρα, ὑπογάστριον, ὑποκοίλιον II 3, 16. λαπάρα III 248,
37. ὑπογάστριον III 14, 40; 314, 41. graece \<λαπάρα\>, pinguedo carnium
(graece *om. R*) *Plac.* V 5, 7 = V 43, 3. pinguedo carnis III 487, 4;
506, 5; V 615, 38. ueretrum V 632, 2. **abdumen** λαπάρα II 358, 45;
506, 22; 528, 46; 529, 6; 546, 47. ὑπογάστριον II 9, 42; III 87, 31;
255, 20. ὑπογάστριον, λίπος III 183, 64. ilium II 564, 7. **abdumine**
id est pinguedine V 652, 3 (= *Iuuenal.* II 86)."""
    ]

CORRECT_PARS = [
r"""<form>Agnina</form> ἄρνειον κρέας <ref addName="Ps.-Cyr."
cRef="CGL.II.245.30">II 245, 30</ref>. ἀρνεία <ref addName="hermen.
Montep." cRef="CGL.III.316.53">III 316, 53</ref>; <ref
cRef="CGL.III.364.29"><ref cRef="CGL.III.364.2">364, 2</ref>9</ref>;
<ref cRef="CGL.III.400.50">400, 50</ref>; <ref
cRef="CGL.III.489.43">489, 43</ref>; <ref cRef="CGL.III.509.9">509,
9</ref>. ἄρνειον <ref addName="hermen. Ps.-Dos. Leid."
cRef="CGL.III.16.6">III 16, 6</ref>; <ref cRef="CGL.III.88.29">88,
29</ref>; <ref cRef="CGL.III.364.2">364, 2</ref>; <ref
cRef="CGL.III.398.3">398, 3</ref>. <form>agminum</form> ἄρνειον <ref
addName="hermen. Monac." cRef="CGL.III.187.40">III 187, 40</ref>; <ref
cRef="CGL.III.255.63">255, 63</ref>.""",

r"""<form>Aeneator</form> σαλπικτής <ref addName="Ps.-Phil."
cRef="CGL.II.12.3">II <ref cRef="CGL.IV.12.3">12, 3</ref></ref>.
tubarum factor <ref addName="gl. nom." cRef="CGL.II.565.22">II 565,
22</ref> (<emph>ubi</emph> cantor <emph>Hildebrand p.</emph> 5.
<emph>male versum</emph>). <form>aenatores</form> κυμβαλοκροῦσται <ref
addName="Ps.-Phil." cRef="CGL.II.12.4">II 12, 4</ref>.
<form>aeneatores</form> tubicines <ref addName="Abstr. II"
cRef="CGL.IV.11.47">IV 11, 47</ref>; <ref cRef="CGL.IV.12.3">12,
3</ref>; <ref cRef="CGL.IV.204.13">204, 13</ref>; V <ref
cRef="CGL.IV.163.48">163, 48</ref>; <ref cRef="CGL.IV.262.48">262,
48</ref>; <ref cRef="CGL.IV.266.47">266, 47</ref>; <ref
cRef="CGL.IV.338.42">338, 42</ref>. <form>aenatores</form> cornicines
<ref addName="Abstr. II" cRef="CGL.IV.12.11">IV 12, 11</ref>.
<form>aeneatores</form> cornic&lt;in&gt;es, liticines, tubicines <ref
addName="Affat." cRef="CGL.IV.475.33">IV 475, 33</ref>.
corni&lt;cin&gt;es, liticines <ref addName="Conscr. gl."
cRef="CGL.V.262.33">V 262, 33</ref>. cornicines, liticines, id est
corno (cornu <emph>de</emph>) uel calamo canentes <ref addName="Abav."
cRef="CGL.IV.306.1">IV 306, 1</ref>; V <ref cRef="CGL.IV.437.46">437,
46</ref> (cornu). corno (cornu <emph>ab</emph>) uel calamo cantantes
<ref addName="Abba" cRef="CGL.IV.204.18">IV 204, 18</ref>. <emph>Cf.
Festus Pauli</emph> 20, 7.""",

r"""<form>Absonus</form> sine sono homo <ref addName="Apod."
cRef="CGL.V.343.31">V 343, 31</ref>; <ref cRef="CGL.V.259.46">259,
46</ref>. <form>absonum</form> ἀπηχές <ref addName="Ps.-Cyr."
cRef="CGL.II.235.7">II 235, 7</ref>. ἀνάρμοστον <ref
addName="Ps.-Phil." cRef="CGL.II.5.21">II 5, 21</ref>; <ref
cRef="CGL.II.554.58">554, 58</ref>. ἀπηχές, ἀμαυρόν <ref addName="gl.
Laud." cRef="CGL.II.555.2">II 555, 2</ref> (<emph>v.</emph> absurdus).
sine sono <ref addName="gl. nom." cRef="CGL.II.563.39">II 563,
39</ref> (= <emph>Non.</emph> 72, 5). <form>absono</form> non simili
sono <ref addName="Abstr. II" cRef="CGL.IV.5.19">IV 5, 19</ref>; <ref
cRef="CGL.IV.202.3">202, 3</ref>. praepostero, absurdo <emph>cod.
Leid.</emph> 67 <emph>E</emph> (<emph>Prodr.</emph> 148). absurdo uel
praepostero <emph>a post</emph> <ref addName="Abstr. II"
cRef="CGL.IV.4.44">IV <ref cRef="CGL.IV.4.44">4, 44</ref></ref>
(propero <emph>cod.</emph>); <ref addName="Abstr. II"
cRef="CGL.IV.4.44">IV <ref cRef="CGL.IV.4.44">4, 44</ref></ref>
(propero <emph>cod.: om. bc</emph>).""",

r"""<form>Abdomen</form> λαπάρα, ὑπογάστριον, ὑποκοίλιον <ref
addName="Ps.-Phil." cRef="CGL.II.3.16">II 3, 16</ref>. λαπάρα <ref
addName="hermen. Einsidl." cRef="CGL.III.248.37">III 248, 37</ref>.
ὑπογάστριον <ref addName="hermen. Ps.-Dos. Leid."
cRef="CGL.III.14.40">III 14, 40</ref>; <ref cRef="CGL.III.314.41">314,
41</ref>. graece &lt;λαπάρα&gt;, pinguedo carnium (graece <emph>om.
R</emph>) <emph>Plac.</emph> V 5, 7 = <ref addName="Plac. lib. rom. /
Plac. lib. gl." cRef="CGL.V.43.3">V 43, 3</ref>. pinguedo carnis <ref
addName="gl. Lois. / Absid. Bern." cRef="CGL.III.487.4">III 487,
4</ref>; <ref cRef="CGL.III.506.5">506, 5</ref>; V <ref
cRef="CGL.III.615.38">615, 38</ref>. ueretrum <ref addName="Abav. mai.
/ Abut." cRef="CGL.V.632.2">V 632, 2</ref>. <form>abdumen</form>
λαπάρα <ref addName="Ps.-Cyr." cRef="CGL.II.358.45">II 358, 45</ref>;
<ref cRef="CGL.II.506.22">506, 22</ref>; <ref
cRef="CGL.II.528.46">528, 46</ref>; <ref cRef="CGL.II.529.6">529,
6</ref>; <ref cRef="CGL.II.546.47">546, 47</ref>. ὑπογάστριον <ref
addName="Ps.-Phil." cRef="CGL.II.9.42">II 9, 42</ref>; III <ref
cRef="CGL.II.87.31">87, 31</ref>; <ref cRef="CGL.II.255.20">255,
20</ref>. ὑπογάστριον, λίπος <ref addName="hermen. Monac."
cRef="CGL.III.183.64">III 183, 64</ref>. ilium <ref addName="gl. nom."
cRef="CGL.II.564.7">II 564, 7</ref>. <form>abdumine</form> id est
pinguedine <ref addName="gl. Iuv." cRef="CGL.V.652.3">V 652, 3</ref>
(= <emph>Iuuenal.</emph> II 86)."""
]

fixed_pars = []
for paragraph in TEST_PARS:
    paragraph = newlines_to_spaces(paragraph)

    paragraph = escape_characters(paragraph)
    paragraph = tag_forms(paragraph)
    paragraph = tag_italics(paragraph)
    paragraph = tag_CGL_refs_new(paragraph)

    fixed_pars.append(paragraph)

with open(outfile, 'w', encoding="utf-8") as f:
    for paragraph in fixed_pars:
        # paragraph += '\n\n'
        wrapped_lines = textwrap.wrap(paragraph)
        f.write('\n'.join(wrapped_lines))
        f.write('\n\n')

for i, paragraph in enumerate(fixed_pars):

    paragraph = textwrap.wrap(paragraph)
    correct_paragraph = textwrap.wrap(newlines_to_spaces(CORRECT_PARS[i]))

    diff = difflib.context_diff(correct_paragraph, paragraph, fromfile='correct_pars', tofile='fixed_pars')
    print('\n'.join(list(diff)))
