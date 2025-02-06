# import torch
# from transformers import T5ForConditionalGeneration, RobertaTokenizer, get_linear_schedule_with_warmup
# from peft import get_peft_model, LoraConfig
# from datasets import load_dataset
#
# # 设置设备（优先使用 CUDA）
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print("当前设备：", device)
# # 加载预训练模型（CodeT5-small）和 tokenizer
# model_name = "D:/PythonCode/CodeBERT/model/CodeT5-small"
# model = T5ForConditionalGeneration.from_pretrained(model_name)
# # 定义 LoRA 配置，实现参数高效微调
# peft_config = LoraConfig(
#     task_type="SEQ_2_SEQ_LM",  # 序列到序列任务
#     r=8,
#     lora_alpha=32,
#     lora_dropout=0.1,
# )
# model = get_peft_model(model, peft_config)
# model.to(device)
#
# tokenizer = RobertaTokenizer.from_pretrained(model_name)
#
# # 加载数据集（这里加载的是 Python 版本）
# ds = load_dataset("google/code_x_glue_ct_code_to_text", "python")
# train_dataset = ds["train"].select(range(1000))
# # 如果数据集太大，可以使用 .select() 限制数据量用于调试，例如：
# # train_dataset = ds["train"].select(range(1000))
#
# # 设置训练参数
# num_epochs = 3  # 根据需要可以增大训练轮次（例如 10、20 或更多）
# learning_rate = 1e-4
# optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
# total_steps = num_epochs * len(train_dataset)
# scheduler = get_linear_schedule_with_warmup(
#     optimizer,
#     num_warmup_steps=int(0.1 * total_steps),
#     num_training_steps=total_steps
# )
#
# # 训练循环
# print("开始训练……")
# for epoch in range(num_epochs):
#     total_loss = 0.0
#     model.train()
#     for i, sample in enumerate(train_dataset):
#         # 使用 dataset 的 code 和 docstring 字段
#         # 这里可以为 code 添加前缀 "summarize: " 帮助模型理解任务（视预训练任务而定）
#         code = "summarize: " + sample["code"]
#         docstring = sample["docstring"]
#
#         # 编码输入和标签（确保进行截断，防止过长）
#         inputs = tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
#         labels = tokenizer(docstring, return_tensors="pt", truncation=True, max_length=128)
#         input_ids = inputs.input_ids.to(device)
#         labels_ids = labels.input_ids.to(device)
#
#         optimizer.zero_grad()
#         outputs = model(input_ids=input_ids, labels=labels_ids)
#         loss = outputs.loss
#         loss.backward()
#         optimizer.step()
#         scheduler.step()
#
#         total_loss += loss.item()
#
#         # 每 100 个样本打印一次当前损失
#         if (i + 1) % 100 == 0:
#             print(f"Epoch {epoch+1}/{num_epochs} - Step {i+1}/{len(train_dataset)} - Loss: {loss.item():.4f}")
#
#     avg_loss = total_loss / len(train_dataset)
#     print(f"Epoch {epoch+1}/{num_epochs} 完成 - 平均损失: {avg_loss:.4f}")
# # 训练完成后，将 LoRA 适配器合并到 CodeT5 模型
# model = model.merge_and_unload()
#
# # 保存完整模型
# model_save_path = "D:/PythonCode/CodeBERT/model/finetuned_codet5_small"
# model.save_pretrained(model_save_path)
# tokenizer.save_pretrained(model_save_path)
#
# print(f"✅ 完整模型已保存到：{model_save_path}")
import torch
from transformers import T5ForConditionalGeneration, RobertaTokenizer, get_linear_schedule_with_warmup
from peft import get_peft_model, LoraConfig
from datasets import load_dataset
from torch.utils.data import DataLoader
from transformers import default_data_collator

# 设置设备（优先使用 CUDA）
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("当前设备：", device)

# 加载预训练模型（CodeT5-small）和 tokenizer
model_name = "D:/PythonCode/CodeBERT/model/CodeT5-small"
model = T5ForConditionalGeneration.from_pretrained(model_name)

# 定义 LoRA 配置
peft_config = LoraConfig(
    task_type="SEQ_2_SEQ_LM",
    r=8,  # LoRA 低秩维度
    lora_alpha=32,
    lora_dropout=0.1,
)
model = get_peft_model(model, peft_config)
model.to(device)

tokenizer = RobertaTokenizer.from_pretrained(model_name)

# 加载数据集
ds = load_dataset("google/code_x_glue_ct_code_to_text", "python")
train_dataset = ds["train"]  # 25 万条数据


# **修正批量预处理函数**
def preprocess_function(sample):
    """对 batch 数据进行预处理"""
    return {
        "input_ids": [tokenizer("summarize: " + c, truncation=True, max_length=256, padding="max_length")["input_ids"]
                      for c in sample["code"]],
        "labels": [tokenizer(d, truncation=True, max_length=64, padding="max_length")["input_ids"] for d in
                   sample["docstring"]]
    }


# **使用 map() 进行批量预处理**
train_dataset = train_dataset.map(preprocess_function, batched=True,
                                  remove_columns=["id", "repo", "path", "func_name", "original_string", "language",
                                                  "code", "code_tokens", "docstring", "docstring_tokens", "sha", "url"])

# **创建 DataLoader**
batch_size = 4
train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=batch_size, collate_fn=default_data_collator)

# **训练参数**
num_epochs = 10
learning_rate = 3e-5
gradient_accumulation_steps = 8

optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
total_steps = len(train_dataloader) * num_epochs
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=int(0.1 * total_steps),
                                            num_training_steps=total_steps)

# **训练循环**
print("🚀 开始训练……")

scaler = torch.cuda.amp.GradScaler()  # FP16 训练

for epoch in range(num_epochs):
    total_loss = 0.0
    model.train()

    for step, batch in enumerate(train_dataloader):
        batch = {k: v.to(device) for k, v in batch.items()}

        with torch.cuda.amp.autocast():  # **启用混合精度**
            outputs = model(**batch)
            loss = outputs.loss / gradient_accumulation_steps  # 处理梯度累积

        scaler.scale(loss).backward()

        if (step + 1) % gradient_accumulation_steps == 0:  # **累积多个 batch 后更新**
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad()
            scheduler.step()

        total_loss += loss.item()

        if (step + 1) % 100 == 0:
            print(f"Epoch {epoch + 1}/{num_epochs} - Step {step + 1}/{len(train_dataloader)} - Loss: {loss.item():.4f}")

    avg_loss = total_loss / len(train_dataloader)
    print(f"✅ Epoch {epoch + 1}/{num_epochs} 完成 - 平均损失: {avg_loss:.4f}")

# **合并 LoRA 适配器并保存完整模型**
model = model.merge_and_unload()
model.save_pretrained("D:/PythonCode/CodeBERT/model/finetuned_codet5_small")
tokenizer.save_pretrained("D:/PythonCode/CodeBERT/model/finetuned_codet5_small")

print(f"✅ 完整模型已保存！")
