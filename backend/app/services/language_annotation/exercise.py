from openai import OpenAI


# -------------------------
# 1. Connect to Ollama
# -------------------------

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


# -------------------------
# 2. Fixed evaluation cases
# -------------------------

test_cases = [
    ("我被扣款两次", "billing"),
    ("发票上的金额不对", "billing"),
    ("按下登录后画面全白", "bug"),
    ("更新后一直闪退", "bug"),
    ("你们周末上班吗", "other"),
    ("谢谢你帮我处理", "other"),
]


# -------------------------
# 3. Call the model
# -------------------------

def ask_model(prompt):
    response = client.chat.completions.create(
        model="gemma4:e4b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()


# -------------------------
# 4. Zero-shot prompt
# -------------------------

def zero_shot_prompt(text):
    return f"""
目标：将客服留言分到 billing、bug 或 other。

资料：
<input_data>{text}</input_data>

规则：
只根据资料分类。
不知道时选 other。

输出：
只返回一个小写标签。
"""


# -------------------------
# 5. Three-shot prompt
# -------------------------

def three_shot_prompt(text):
    return f"""
目标：将客服留言分到 billing、bug 或 other。

资料：
<input_data>{text}</input_data>

规则：
只根据资料分类。
不知道时选 other。

范例：

输入：信用卡又扣了一次
输出：billing

输入：提交表单后没有反应
输出：bug

输入：可以更改联系邮箱吗
输出：other

输出：
只返回一个小写标签。
"""


# -------------------------
# 6. Evaluate a prompt
# -------------------------

def evaluate(prompt_function):
    correct = 0

    for text, expected in test_cases:
        prompt = prompt_function(text)

        prediction = ask_model(prompt)

        print("Input:     ", text)
        print("Expected:  ", expected)
        print("Prediction:", prediction)

        if prediction == expected:
            correct += 1
            print("✅ Correct")
        else:
            print("❌ Wrong")

        print("-" * 40)

    print(f"Score: {correct} / {len(test_cases)}")

    return correct


# -------------------------
# 7. Run the experiment
# -------------------------

print("\nZERO-SHOT")
print("=" * 40)

zero_score = evaluate(zero_shot_prompt)


print("\nTHREE-SHOT")
print("=" * 40)

three_score = evaluate(three_shot_prompt)


print("\nRESULT")
print("=" * 40)
print(f"Zero-shot:  {zero_score} / 6")
print(f"Three-shot: {three_score} / 6")