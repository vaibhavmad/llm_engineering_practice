# task is to complete the day 1 task and use a local LLM to complete it
from openai import OpenAI


OLLAMA_BASE_URL = 'http://localhost:11434/v1'
ollama = OpenAI(base_url=OLLAMA_BASE_URL, api_key='ollama')

system_prompt = """
You are a research article summarizer. Your job is to make any research article understandable to a complete layman — someone with no background in the field.

Priority order (when these conflict, the higher one wins):
1. Plain-language clarity — a non-expert must be able to read this and understand it in one pass.
2. Accuracy of the core message — the main question, finding, and why it matters must be correct.
3. Completeness — it is OK to drop details, statistics, methodology, and nuance if keeping them would hurt clarity.

Rules:
- Do not use jargon, abbreviations, or technical terms. If a technical concept is essential to the finding, explain it using a simple real-world analogy instead of the original term.
- Do not include specific statistics, p-values, confidence intervals, or methodological detail unless a number is the entire point of the finding (e.g., "twice as likely") — and even then, round and simplify it.
- Preserve the article's actual level of certainty in plain words. If the article says a result "suggests" or "is consistent with" something (rather than proving it), say "this suggests..." or "points to..." — don't state it as a hard fact.
- Structure the summary however best fits the article — you decide the format (straight prose, short lines, or light bullets). Prioritize what reads most naturally, not a fixed template.
- Target length: roughly 100–200 words. Stay short even if the article is dense; cut detail rather than expand.
- Do not editorialize or add claims, context, or implications not present in the article.

If you deviate from any of the above rules for a given article (e.g., because the article is too short, too ambiguous, or unsummarizable as instructed), state the reason briefly at the very top, before the summary.
"""

user_prompt = """
Please summarize the below article:

Pervasive Cis-Regulatory Epistasis Modulates Penetrance of Hypomorphic Loss-of-Function Alleles at the FOXP2-CNTNAP2 Regulatory Axis: A Multi-Omic Reanalysis
Abstract
Genome-wide association studies have repeatedly implicated the FOXP2-CNTNAP2 regulatory axis in neurodevelopmental phenotypes, yet variance in penetrance among carriers of identical coding variants remains poorly explained by additive polygenic models. Here we leverage long-read haplotype-resolved assemblies (n=1,847) integrated with single-cell ATAC-seq and Hi-C contact maps across 14 fetal cortical cell types to demonstrate that penetrance of a recurrent FOXP2 hypomorphic allele (c.1313A>G, p.Arg438His) is conditionally buffered by cis-acting structural haplotypes at a topologically associating domain (TAD) boundary 340kb distal to the CNTNAP2 transcriptional start site. Allele-specific expression analysis reveals that carriers harboring the ancestral CTCF-binding motif configuration (rs2710102-linked haplotype block) exhibit incomplete penetrance (18.3%, 95% CI: 12.1–26.4%) relative to carriers of the derived motif-disrupting haplotype (penetrance 71.6%, 95% CI: 64.2–78.1%), independent of trans-acting polygenic background as estimated by LDpred2-derived burden scores. Mendelian randomization using cis-eQTL instruments (F-statistic = 47.3) supports a causal—rather than confounded—relationship between TAD boundary insulation strength and downstream haploinsufficiency buffering. These findings reframe the FOXP2-CNTNAP2 axis not as a simple monogenic-modifier system but as an emergent property of three-dimensional chromatin architecture acting as a stochastic penetrance rheostat, with implications for the broader interpretation of "incomplete penetrance" in ACMG variant classification frameworks.
Introduction
The classical interpretation of Mendelian penetrance assumes a relatively static genotype-phenotype mapping, perturbed primarily by stochastic developmental noise or unmeasured trans-acting polygenic background (Zuk et al., 2014; Wright et al., 2019). This framework, however, has proven increasingly inadequate for explaining the substantial phenotypic discordance observed among monozygotic twin pairs discordant for autism spectrum disorder despite genetically identical coding sequence at high-confidence risk loci (SFARI Gene tier 1S genes), a discordance rate that cannot be parsimoniously attributed to environmental exposure differentials alone given concordance studies of the broader autism phenome (Tick et al., 2016).
Recent advances in long-read sequencing technology (PacBio HiFi, Oxford Nanopore Duplex) combined with chromosome conformation capture methodologies have begun to resolve structural haplotype variation invisible to short-read GWAS scaffolding—particularly at TAD boundaries, where CTCF/cohesin-mediated loop extrusion establishes insulated neighborhoods that constrain enhancer-promoter contact frequency (Dixon et al., 2012; Rao et al., 2014). We hypothesized that cryptic structural variation at such boundaries, segregating independently of the focal coding variant due to recombination hotspot decoupling, could function as a cis-modifier of penetrance—effectively a "volume knob" on haploinsufficiency rather than a binary modifier.
Methods (abridged)
Cohort ascertainment. Probands (n=1,847) were drawn from the SPARK and SSC cohorts, restricted to confirmed carriers of FOXP2 c.1313A>G via clinical exome reanalysis, with informed consent obtained under protocol IRB-2019-4471.
Haplotype phasing. Long-read assemblies were phased using a hidden Markov model trio-binning approach (HiFiasm v0.19.5) with downstream haplotype-resolved TAD calling via HiCExplorer, applying an insulation score threshold of |Δ| > 0.4 to call boundary disruption events.
Allele-specific expression. scATAC-seq libraries (10x Genomics Multiome) were generated from cortical organoids (day 45 and day 90 differentiation timepoints) derived from a subset of carriers (n=62) with available iPSC lines, with ASE quantified via WASP-corrected read counting to mitigate reference mapping bias.
Statistical framework. Penetrance estimates were modeled using a Bayesian hierarchical logistic regression with haplotype block as a random effect nested within ascertainment cohort, implemented in Stan (rstanarm), with weakly informative Cauchy priors (scale=2.5) on log-odds coefficients to regularize against complete separation given sparse cell counts in minor haplotype strata.
Results (excerpt)
Insulation score disruption at the distal TAD boundary (chr7:113,743,221–113,744,890, GRCh38) was significantly associated with increased CNTNAP2 allelic imbalance in trans to the FOXP2 hypomorphic allele (β=0.84, SE=0.11, p=3.2×10⁻¹⁴), consistent with a model in which loss of insulator function permits ectopic enhancer hijacking from a neighboring developmentally-silenced super-enhancer cluster, thereby exacerbating CNTNAP2 transcriptional dysregulation beyond what is attributable to the FOXP2 variant in isolation. Critically, this effect persisted after conditioning on a 312-variant polygenic burden score (partial R²=0.09 vs. 0.31 for haplotype status alone), suggesting the structural mechanism is largely orthogonal to additive trans-acting risk.
"""

messages = [
    {'role': 'system', 'content': system_prompt},
    {'role': 'user', 'content': user_prompt}
]

response = ollama.chat.completions.create(model='llama3.2', messages=messages)
print(response.choices[0].message.content)

"""
Response:
The study explored how genetics affect brain development and behavior using two genes, FOXP2 and CNTNAP2. These genes usually work together in a straightforward way, but some carriers of a mutation (c.1313A>G) in the FOXP2 gene don't always develop problems. The researchers wanted to know if something else was adding to this problem.

They looked at a group of 1,847 people who carried the mutation and found that those with certain structures of their chromosomes near the CNTNAP2 gene were more or less likely to have developmental problems. In simple terms, it's like a "volume knob" on how intense the haploinsufficiency (a term they used) is.

The study supports a new idea: instead of thinking that genetics are in all-or-nothing categories, maybe there's a spectrum of effects based on where something goes wrong on the chromosomes.
"""