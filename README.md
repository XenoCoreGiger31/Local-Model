---
license: apache-2.0
base_model:
- Qwen/Qwen2.5-1.5B-Instruct
pipeline_tag: text-generation
---
# Model Card for Model ID

Large language Model(LLM) qwen2.5-1.5b-q4 quantized-ABLITERATED for iOS mobile.

## Model Details

These models were fine tuned from original base model (QWEN2.5-1.5b Instruct-ABLITERATED) QWEN2.5-1.5B Instruct safetensors/q8/q4

### Model Description
Qwen 2.5-1.5B is a compact, high-performance large language model optimized for local inference on resource-constrained devices, particularly iOS mobile platforms. This release provides three quantization variants—SafeTensors (full precision base), Q8 (8-bit), and Q4 (4-bit)—enabling flexible deployment across different hardware configurations while maintaining inference speed and output quality.

Developed for cybersecurity applications, coding tasks, and uncensored dialogue, this model prioritizes privacy-first inference without internet connectivity. It is designed for users who require on-device LLM capabilities with minimal external dependencies, making it ideal for penetration testing automation, local development workflows, and private mobile AI assistants.





- **Developed by:** automajicly
- **Funded by [optional]:** [More Information Needed]
- **Shared by [optional]:** [More Information Needed]
- **Model type:** Large Language Model(LLM)
- **Language(s) (NLP):** NLP (English)
- **License:** Apache 2.0
- **Finetuned from model [optional]:** QWEN2.5-1.5b-Instruct

### Model Sources [optional]



- **Repository:** https://huggingface.co/automajicly/Local-Model

## Uses

<!-- Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model. -->

### Direct Use

This model is designed for local, on-device inference without requiring external API calls or internet connectivity. Primary use cases include:

1. **Local LLM Inference via Mobile Apps** – Deploy via PocketPal AI, Off-Grid, or similar iOS LLM clients for real-time dialogue and task automation on iPhone without cloud dependencies.

2. **Cybersecurity Education and Threat Analysis** – Generate detailed step-by-step explanations of attack vectors (e.g., Wi-Fi compromise, network exploitation), defensive strategies, and system hardening procedures. Useful for learning penetration testing methodologies, VM configuration, and Linux security fundamentals.

3. **Development and Automation** – Use for code generation, debugging Python scripts, system administration tasks, and technical problem-solving in offline or air-gapped environments.

All inference runs locally on-device with no data transmission to external servers.

### Downstream Use [optional]

This model is intended to be fine-tuned, quantized further, or integrated into custom applications and workflows. Users are encouraged to:

- Adapt the model for domain-specific tasks (cybersecurity, coding, mobile deployment)
- Further quantize to Q3 or lower for additional mobile optimization
- Integrate into custom LLM applications or security automation frameworks
- Modify, improve, and redistribute with appropriate attribution

If you create an improved version or novel application, please share your work and credit the original Qwen 2.5-1.5B base model and this repository.

### Out-of-Scope Use

<!-- This section addresses misuse, malicious use, and uses that the model will not work well for. -->

[More Information Needed]

## Bias, Risks, and Limitations

**Model Size and Capability Limitations:**
This is a 1.5B parameter model optimized for mobile inference. While performant on resource-constrained devices, it may lack the nuance, reasoning depth, and knowledge breadth of larger models (7B+). Complex multi-step reasoning or highly specialized tasks may exceed its design scope.

**Uncensored Nature:**
This model is intentionally uncensored and will generate detailed responses to requests that larger, safety-filtered models would refuse. Users are responsible for prompt engineering and filtering outputs appropriately. Do not use for generating malicious content, actual hacking, or illegal activities.

**Mobile App Dependency:**
Inference requires a third-party iOS LLM client (e.g., PocketPal AI). Currently tested and validated on PocketPal AI. Compatibility with other apps (Off-Grid, etc.) is still being evaluated. Performance and behavior may vary across different client implementations.

**Privacy Considerations:**
While inference is local and does not transmit data externally, users should understand that their prompts and model outputs remain on-device only if the app itself does not log or sync data to cloud services.


### Recommendations
1. **Use PocketPal AI** – Currently validated and optimized for PocketPal AI on iOS. Install from the App Store, load the model via local file or HuggingFace integration.

2. **Start with Q4 Quantization** – For iPhone 13 and similar devices, the Q4 variant (1.12 GB) offers the best balance of speed and quality. Only use SafeTensors or Q8 if you have sufficient device storage and RAM.

3. **Test on Local Network** – Ensure your iPhone and inference device (if separate) are on the same network for fastest performance. No internet required—purely local inference.

4. **Prompt Engineering** – This model responds well to detailed, structured prompts. Provide context and specificity for best results (e.g., "Step-by-step explanation of..." vs. vague queries).

5. **Monitor App Compatibility** – Currently testing compatibility with Off-Grid and other LLM clients. Check back for updates on broader app support.


Users (both direct and downstream) should be made aware of the risks, biases and limitations of the model. More information needed for further recommendations.

## How to Get Started with the Model

1. Download your preferred quantization (Q4, Q8, or SafeTensors) from this repository.
2. Install PocketPal AI from the App Store.
3. Open PocketPal AI → Add Model → Select local file → Choose your downloaded model.
4. Start a new chat and begin using the model locally on-device.

For advanced users: Models can also be integrated into custom inference pipelines via llama.cpp or similar frameworks supporting GGUF formats.


## Training Details

### Training Data
This model is a quantized derivative of Qwen 2.5-1.5B-Instruct. It inherits the training data and methodology from the original Qwen 2.5 model. For detailed information on the base model's training data, architecture, and training procedures, refer to the official Qwen repository: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct


### Training Procedure

<!-- This relates heavily to the Technical Specifications. Content here should link to that section when it is relevant to the training procedure. -->

#### Preprocessing [optional]

[More Information Needed]


#### Training Hyperparameters

- **Training regime:** [More Information Needed] <!--fp32, fp16 mixed precision, bf16 mixed precision, bf16 non-mixed precision, fp16 non-mixed precision, fp8 mixed precision -->

#### Speeds, Sizes, Times [optional]

<!-- This section provides information about throughput, start/end time, checkpoint size if relevant, etc. -->

[More Information Needed]

## Evaluation

<!-- This section describes the evaluation protocols and provides the results. -->

### Testing Data, Factors & Metrics

#### Testing Data

Based on QWEN2.5-1.5b-Instruct training data

#### Factors

<!-- These are the things the evaluation is disaggregating by, e.g., subpopulations or domains. -->

[More Information Needed]

#### Metrics

<!-- These are the evaluation metrics being used, ideally with a description of why. -->

[More Information Needed]

### Results

[More Information Needed]

#### Summary



## Model Examination [optional]

<!-- Relevant interpretability work for the model goes here -->

[More Information Needed]

## Environmental Impact

<!-- Total emissions (in grams of CO2eq) and additional considerations, such as electricity usage, go here. Edit the suggested text below accordingly -->

Carbon emissions can be estimated using the [Machine Learning Impact calculator](https://mlco2.github.io/impact#compute) presented in [Lacoste et al. (2019)](https://arxiv.org/abs/1910.09700).

- **Hardware Type:** [More Information Needed]
- **Hours used:** [More Information Needed]
- **Cloud Provider:** [More Information Needed]
- **Compute Region:** [More Information Needed]
- **Carbon Emitted:** [More Information Needed]

## Technical Specifications [optional]

### Model Architecture and Objective

[More Information Needed]

### Compute Infrastructure

[More Information Needed]

#### Hardware

[More Information Needed]

#### Software

[More Information Needed]

## Citation [optional]

<!-- If there is a paper or blog post introducing the model, the APA and Bibtex information for that should go in this section. -->

**BibTeX:**

[More Information Needed]

**APA:**

[More Information Needed]

## Glossary [optional]

<!-- If relevant, include terms and calculations in this section that can help readers understand the model or model card. -->

[More Information Needed]

## More Information [optional]

[More Information Needed]

## Model Card Authors [optional]

[More Information Needed]

## Model Card Contact

christophersheridan@gmail.com or huggingface.co/automajicly/Local-Model