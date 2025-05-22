import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import jieba
import numpy as np

# ======== 配置参数 ========
MODEL_PATH = "./intentionmodel/results4english"  # 模型保存目录
ONNX_PATH = "./intentionmodel/model.onnx"       # ONNX模型保存路径
LABEL_MAP = {0: "vector_db", 1: "neo4j", 2: "other"}
MAX_LENGTH = 64  # 与训练时保持一致

# ======== 初始化模型和分词器 ========
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载分词器（需添加领域词汇）
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH, local_files_only=True).to(device)

# ======== 导出ONNX模型 ========
def export_onnx():
    # 设置为评估模式
    model.eval()
    
    # 创建虚拟输入
    dummy_text = "example query"
    inputs = tokenizer(
        dummy_text,
        max_length=MAX_LENGTH,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )
    
    # 将输入移到对应设备
    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)
    
    # 导出模型
    torch.onnx.export(
        model,
        (input_ids, attention_mask),
        ONNX_PATH,
        input_names=["input_ids", "attention_mask"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "logits": {0: "batch_size"}
        },
        opset_version=14,
        do_constant_folding=True
    )
    print(f"ONNX模型已导出到：{ONNX_PATH}")

# ======== 预测函数 ========
def predict(text):
    # 预处理
    inputs = tokenizer(
        text,
        max_length=MAX_LENGTH,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    ).to(device)
    
    # 推理
    with torch.no_grad():
        outputs = model(**inputs)
    
    # 解析结果
    probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]
    pred_label = np.argmax(probs)
    
    return {
        "text": text,
        "intent": LABEL_MAP[pred_label],
        "confidence": float(probs[pred_label]),
        "details": {LABEL_MAP[i]: float(probs[i]) for i in range(len(LABEL_MAP))}
    }

# ======== 交互测试 ========
if __name__ == "__main__":
    # 导出ONNX模型
    export_onnx()
    
    # print("\n输入'q'退出测试")
    # while True:
    #     text = input("\n请输入问题：")
    #     if text.lower() == 'q':
    #         break
            
    #     result = predict(text)
    #     print(f"\n预测结果：{result['intent']}（置信度：{result['confidence']:.2%}）")
    #     print("详细概率：")
    #     for k, v in result["details"].items():
    #         print(f"  {k}: {v:.2%}")