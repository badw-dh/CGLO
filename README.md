# Corpus Glossariorum Latinorum Online (CGLO)

This repository contains the data for
[Goetz’s Corpus Glossariorum Latinorum Online](https://publikationen.badw.de/en/cglo/index) (*CGLO*).

Its core consists of a digitized version of G. Goetz et al., *Corpus glossariorum Latinorum* (*CGL*; Leipzig: Teubner, 1888–1923), volumes VI and VII, in XML and markdown formats. These two volumes contain the *Thesaurus glossarum*, a lemmatized index to the entire corpus, divided into sections by lemma language: Latin (VI 1-VII 433), Greek (VII 441-687), Old English (VII 689-712), and Old High German (VII 712). Three sections of corrigenda and addenda have also been included (VI praef. p. ix-x; VI 753-754; VII 434-438).

OCR texts of the volumes were manually corrected by hand and converted into markdown. The markdown in turn is automatically converted into XML.
> :warning: **NB**: At this stage of the project, the manual correction has focused on the lemmata, Greek words, and sequences of internal cross-references. Many errors remain and will be corrected in subsequent releases.

The repository is structured as follows:
- "markdown" directory: corrected markdown files by page
- "markdown-combined" directory: corrected markdown files combined into sections and as complete file ("CGLO.99.combined.mkd")
- "XML" directory: XML files by section and as complete file ("CGLO.99.combined.xml")
- "JSON" directory: JSON data used for searchable web interface
- "scripts" directory: Python scripts used to clean the markdown files and generate XML output

Minor divergences from the printed volumes, including manually corrected errata, are described in DIFFERENTIAE.docx. The XML scheme is described in schema-CGLO.xml.

## License

All data in this repository is licensed under the [Creative Commons CC-BY 4.0 International License](https://creativecommons.org/licenses/by/4.0/deed.en).

## Version

The current version is **v2024-01**, released on January 24, 2024. Releases are numbered in [YEAR]-[MONTH] format.

## Citation

For any specific version of this data, please use the permanent link: https://daten.badw.de/CGLO/-/tree/VERSION
where "VERSION" should be substituted by the particular version you intend to cite.

For the most current version, please, use the link: https://daten.badw.de/CGLO/-/tree/main

Citations of *CGLO* should be checked against the print *CGL* for accuracy (minor divergences and errata are described in DIFFERENTIAE.docx). Images of the relevant pages are provided in the *CGLO* interface.

To cite an entry from the *Thesaurus glossarum* we recommend any of the following conventions:
- *CGLO* s.v. *Abacus* [version 2024-01]  (to cite the entry [Abacus] (https://publikationen.badw.de/en/cglo/index#14) explicitly according to *CGLO* data)
- *CGL* s.v. *Abacus*  # (to cite the same entry according to the printed *CGL*)
- *GLOSS.* s.v. *Abacus*  # (the same using *TLL*-style conventions)

> :memo: **NB**: *CGL* capitalizes the lemmata of all main entries (e.g. *Abacus*) to distinguish them from sub-lemmata (e.g. *abaci*), which are only capitalized when proper names. In the XML data every \<form\> tag receives a unique @id element that can be used for reference as long as the version is explicitly stated. The id element may vary from version to version.

Occurrences from individual glossaries, printed in volumes II to V, are typically cited by volume and line number according to the following format:
- *CGL* II 215, 2  (the equivalence *abacus* ἄβαξ found in volume II, page 215, line 2)
- *CGL* II.215.2  (the same using dots for spaces and commas)
- *GLOSS.* II 215, 2  (the same using *TLL*-style conventions)

A bibtex entry for *CGLO*:

	`@misc{CGLO,
		title 			= "CGLO",
		author			= "Goetz, Georg and Gitner, Adam, et al."
		howpublished	= "\url{https://publikationen.badw.de/en/cglo/index}",
		edition			= "23-12"
		}`

## Authors and Contributors

The corpus was digitized under the direction of Dr. Adam Gitner with the following main contributors: Dr. Alessia Pezzella, Dr. Andrea Consalvi, Javier Agredo, and Bertold Carl Ammer. Dr. Franck Cinato provided invaluable guidance, including advice about the XML scheme, and the *CGL* table of contents.

## Curator

This repository is provided by the Bavarian Academy of Sciences and Humanities. For content or technical issues please contact agitner@thesaurus.badw.de or digitalisierung@badw.de.

The data has been produced for the [Thesaurus Linguae Latinae](https://thesaurus.badw.de/), the most comprehensive ancient Latin dictionary, hosted by the [Bavarian Academy of Sciences and Humanities](https://badw.de).

## Acknowledgments

The digitization was funded by the [Text+ Initiative] (https://text-plus.org/en/) and supported by the Lexical Resources collection.
The print copies of *CGL* in the TLL library were scanned at the initiative of Dr. Franck Cinato with funding from the Centre national de la recherche scientifique, UMR 7597 [Laboratoire d'Histoire des Théories Linguistiques] (https://htl.cnrs.fr/).
The XML scheme follows closely the format provided by the [Thesaurus Glossariorum project] (https://htldb.huma-num.fr/exist/apps/htldb/elma/thegloss/home.html).
Resources and coordination were provided by the Thesaurus Linguae Latinae and the IT Department of the Bavarian Academy of Sciences and Humanities (esp. Dr. Eckhart Arnold and Dr. Stefan Müller).
For more information please read the [website] (https://publikationen.badw.de/en/cglo/index).
