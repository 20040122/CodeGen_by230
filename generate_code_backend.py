from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
import logging

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 初始化 FastAPI 应用
app = FastAPI()


# 模型加载函数
def load_model(model_path):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型路径未找到: {model_path}")

    logger.debug(f"加载模型路径: {model_path}")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = tokenizer.eos_token_id

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    return tokenizer, model, device


# 加载模型
model_path = r"D:\PythonCode\CodeBERT\model\codegen"
tokenizer, model, device = load_model(model_path)


# 定义请求数据模型
class FunctionRequest(BaseModel):
    function_name: str


class CodeCompletionRequest(BaseModel):
    prompt: str


# 生成函数代码的函数
def generate_function_code(function_name, tokenizer, model, device, max_new_tokens=200):
    prompt = f"# 生成一个名为 {function_name} 的 Python 函数。\n\ndef {function_name}("
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

    try:
        with torch.no_grad():
            output_ids = model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                temperature=0.3,
                top_p=0.9,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id,
                num_return_sequences=1,
                do_sample=True
            )
        generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        function_code_start = generated_text.find(f"def {function_name}")
        if function_code_start != -1:
            function_code = generated_text[function_code_start:]
            end_index = function_code.find('\n\n')
            if end_index != -1:
                function_code = function_code[:end_index]
            return function_code.strip()
    except Exception as e:
        logger.error(f"Error in generate_function_code: {e}")
        return ""
    return ""


# 代码补全的函数
def complete_code(tokenizer, model, prompt, device, max_length=300, top_p=0.90, top_k=30, temperature=0.3):
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    try:
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=max_length,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=True,
                top_p=top_p,
                top_k=top_k,
                temperature=temperature
            )

        completed_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
        prompt_length = len(prompt)
        generated_text = completed_code[prompt_length:]
        stop_pos = generated_text.find("def ")
        if stop_pos != -1:
            completed_code = completed_code[:prompt_length + stop_pos]
        return completed_code
    except Exception as e:
        logger.error(f"Error in complete_code: {e}")
        return ""


@app.post("/generate_code/")
async def generate_code(request: FunctionRequest):
    logger.debug("生成函数代码路由被触发")
    function_name = request.function_name.strip()
    if not function_name.isidentifier():
        raise HTTPException(status_code=400, detail="无效的函数名")
    try:
        function_code = generate_function_code(function_name, tokenizer, model, device)
        if not function_code:
            raise HTTPException(status_code=500, detail="未能生成有效的函数代码")
    except Exception as e:
        logger.error(f"生成函数代码时出错: {e}")
        raise HTTPException(status_code=500, detail=f"生成函数代码时出错: {str(e)}")

    return {"function_name": function_name, "generated_code": function_code}


# 路由：代码补全
@app.post("/complete_code/")
async def code_completion(request: CodeCompletionRequest):
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="提示不能为空")

    try:
        completed_code = complete_code(
            tokenizer,
            model,
            prompt,
            device,
            max_length=300,  # 默认值
            top_p=0.90,  # 默认值
            top_k=30,  # 默认值
            temperature=0.3  # 默认值
        )
        if not completed_code:
            raise HTTPException(status_code=500, detail="未能生成有效的补全代码")
    except Exception as e:
        logger.error(f"生成代码时出错: {e}")
        raise HTTPException(status_code=500, detail=f"生成代码时出错: {str(e)}")

    return {"prompt": prompt, "completed_code": completed_code}

print(app.routes)  # 打印所有路由
