#!/usr/bin/env python3
"""Insert outreach messages for batch of channels into the SQLite database."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db

messages = []

# ============================================================================
# RUSSIAN CHANNELS
# ============================================================================

# 1. @hiaimedia (2.35M subs, "Hi, AI - Новости технологий", casual, admin @hiai_ads)
messages.append(("hiaimedia", """Привет! Видел ваш пост про учителей и гранты от Т-Банка, вообще крутой канал, 2 миллиона подписчиков на tech-новостях и подача при этом живая, без душного корпоратива.

tl;dr: Собрал инструмент, который делает AI реально надёжным. 120+ моделей, 9 стадий, слепой peer review, adversarial атаки, проверка фактов по живому вебу. Не очередная обёртка. Пайплайн уничтожения галлюцинаций. И отзывы сносят крышу.

Как это работает: выбираешь три модели из 120+ (Anthropic, OpenAI, Google, xAI, Meta, Mistral, DeepSeek, Qwen). Они отвечают независимо, потом вслепую рецензируют друг друга. Выживший ответ проходит adversarial refinement, проверку фактов по вебу и devil's advocate. Разные данные для обучения = разные ошибки. Это не теория, это механизм.

Бесплатная подписка, если хочешь потестить. Я Маартен, соло-разработчик из Голландии.

https://triall.ai?lng=ru&utm_source=telegram&utm_medium=outreach&utm_campaign=hiaimedia""", "ru"))

# 2. @neuraldvig (327K subs, "Нейродвиж", casual, admin @todaycast)
messages.append(("neuraldvig", """Привет! Видел пост про то, что AI в бизнесе уже не конкурентное преимущество, а базовая линия. Полностью согласен, и именно из этого родилась идея Triall.

tl;dr: Собрал инструмент, который делает AI реально надёжным. 120+ моделей, 9 стадий, слепой peer review, adversarial атаки, проверка фактов по живому вебу. Не очередная обёртка. Пайплайн уничтожения галлюцинаций. И отзывы сносят крышу.

Если AI уже baseline, то качество ответов становится единственным дифференциатором. Выбираешь три модели из 120+, они отвечают независимо, потом вслепую рвут друг друга на части. Adversarial refinement, проверка фактов по вебу, devil's advocate. Разные архитектуры = разные слепые зоны. Вот и весь секрет.

Бесплатная подписка, чтобы попробовать. Я Маартен, соло-разработчик из Голландии, буду рад обратной связи.

https://triall.ai?lng=ru&utm_source=telegram&utm_medium=outreach&utm_campaign=neuraldvig""", "ru"))

# 3. @gptpublic (286K subs, "ChatGPT | Нейросети", casual)
messages.append(("gptpublic", """Привет! Читаю канал давно, посты про VPN-ситуацию в России и новости ChatGPT всегда в точку. Аудитория у вас мощная и вовлечённая.

tl;dr: Собрал инструмент, который делает AI реально надёжным. 120+ моделей, 9 стадий, слепой peer review, adversarial атаки, проверка фактов по живому вебу. Не очередная обёртка. Пайплайн уничтожения галлюцинаций. И отзывы сносят крышу.

Проблема ChatGPT (и любого одного AI) в том, что он соглашается с тобой, даже когда врёт. Triall это исправляет: три модели из 120+ отвечают независимо, вслепую рецензируют друг друга, потом adversarial refinement, проверка фактов по вебу, devil's advocate. Разные данные обучения = разные ошибки. Одна модель промахнётся, другие поймают.

Бесплатная подписка, если интересно потестить. Я Маартен, соло-разработчик из Голландии.

https://triall.ai?lng=ru&utm_source=telegram&utm_medium=outreach&utm_campaign=gptpublic""", "ru"))

# 4. @neuralshit (51.1K subs, "Neural Shit", casual, admin @krasniy_doshik)
messages.append(("neuralshit", """Йоу! «Вы недостаточно молитесь» и вообще подача в канале огонь, мемы про AI на таком уровне мало кто делает. Серьёзно.

tl;dr: Собрал инструмент, который делает AI реально надёжным. 120+ моделей, 9 стадий, слепой peer review, adversarial атаки, проверка фактов по живому вебу. Не очередная обёртка. Пайплайн уничтожения галлюцинаций. И отзывы сносят крышу.

Короче, все AI сейчас работают по принципу «одна модель, один ответ, и молись чтоб не наврал». Triall другой: три модели из 120+ отвечают независимо, вслепую рвут друг друга, потом adversarial refinement, проверка фактов по вебу и devil's advocate. Когда все три уверенно соглашаются без доказательств, система флагает это отдельно. Уверенный консенсус без пруфов опаснее очевидного бреда.

Бесплатная подписка, если хочешь глянуть. Я Маартен, соло-дев из Голландии.

https://triall.ai?lng=ru&utm_source=telegram&utm_medium=outreach&utm_campaign=neuralshit""", "ru"))

# 5. @cgevent (49.3K subs, "Метаверсище и ИИще", casual, admin @SergeyTsyptsyn)
messages.append(("cgevent", """Привет, Сергей! Канал «Метаверсище и ИИще» уникальный, мало кто совмещает метаверс-тематику с AI-контентом. Пост про Runway и видеогенерацию зацепил.

tl;dr: Собрал инструмент, который делает AI реально надёжным. 120+ моделей, 9 стадий, слепой peer review, adversarial атаки, проверка фактов по живому вебу. Не очередная обёртка. Пайплайн уничтожения галлюцинаций. И отзывы сносят крышу.

Суть простая: выбираешь три модели из 120+ по 8 семействам. Разные данные обучения, разные слепые зоны. Отвечают независимо, потом вслепую рецензируют друг друга. Adversarial refinement, проверка фактов по живому вебу, devil's advocate, который пытается разнести всё что осталось.

Бесплатная подписка, если интересно. Я Маартен, соло-разработчик из Голландии.

https://triall.ai?lng=ru&utm_source=telegram&utm_medium=outreach&utm_campaign=cgevent""", "ru"))

# 6. @strangedalle (43.4K subs, "Ai molodca", casual, admin @dobrokotov_work)
messages.append(("strangedalle", """Привет! Канал «Ai molodca» реально выделяется, контент про AI-генерацию изображений и видео на уровне, а пост про Seedance2 был топ.

tl;dr: Собрал инструмент, который делает AI реально надёжным. 120+ моделей, 9 стадий, слепой peer review, adversarial атаки, проверка фактов по живому вебу. Не очередная обёртка. Пайплайн уничтожения галлюцинаций. И отзывы сносят крышу.

Генерация картинок и видео это круто, но когда нужны точные ответы, один AI часто врёт уверенно. Triall решает именно это: три модели из 120+ отвечают независимо, вслепую рецензируют друг друга, проходят adversarial refinement и проверку фактов по живому вебу. Разные архитектуры = разные ошибки = надёжный результат.

Бесплатная подписка, если хочешь попробовать. Я Маартен, соло-дев из Голландии.

https://triall.ai?lng=ru&utm_source=telegram&utm_medium=outreach&utm_campaign=strangedalle""", "ru"))

# 7. @llm_under_hood (24.6K subs, "LLM под капотом", technical)
messages.append(("llm_under_hood", """Привет! «LLM под капотом» один из лучших технических каналов про LLM на русском. Нравится, что копаете в механику, а не просто новости пересказываете.

tl;dr: Собрал инструмент, который делает AI реально надёжным. 120+ моделей, 9 стадий, слепой peer review, adversarial атаки, проверка фактов по живому вебу. Не очередная обёртка. Пайплайн уничтожения галлюцинаций. И отзывы сносят крышу.

Раз вы разбираетесь в архитектуре LLM, вот core insight: разные модели галлюцинируют по-разному из-за разных тренировочных данных. Triall использует это, три модели из 120+ отвечают независимо, потом слепой peer review. Выживший ответ проходит adversarial refinement, claim verification по живому вебу и devil's advocate. Основано на H-Neurons paper (Tsinghua, arXiv 2512.01797).

Бесплатная подписка, если интересно разобрать изнутри. Я Маартен, соло-разработчик из Голландии.

https://triall.ai?lng=ru&utm_source=telegram&utm_medium=outreach&utm_campaign=llm_under_hood""", "ru"))

# 8. @isimplify (19.4K subs, "iSimplify", casual, admin @Noelllh)
messages.append(("isimplify", """Привет! Канал iSimplify реально полезный, обзоры AI-инструментов и сервисов без воды. Именно то, что людям нужно.

tl;dr: Собрал инструмент, который делает AI реально надёжным. 120+ моделей, 9 стадий, слепой peer review, adversarial атаки, проверка фактов по живому вебу. Не очередная обёртка. Пайплайн уничтожения галлюцинаций. И отзывы сносят крышу.

Для обзора AI-инструментов Triall может быть интересной темой: не чат-бот, а пайплайн. Три модели из 120+ отвечают независимо, вслепую рецензируют друг друга. Потом adversarial refinement, проверка фактов по вебу и devil's advocate. Если все три уверенно согласились без доказательств, система это ловит отдельно.

Бесплатная подписка, если хочешь потестить и разобрать для канала. Я Маартен, соло-разработчик из Голландии.

https://triall.ai?lng=ru&utm_source=telegram&utm_medium=outreach&utm_campaign=isimplify""", "ru"))

# 9. @misha_davai_po_novoi (17.7K subs, "Миша, давай по новой", casual, admin @pleeeksss)
messages.append(("misha_davai_po_novoi", """Привет, Миша! Канал огонь, AI для начинающих в такой подаче мало кто делает. Название вообще гениальное.

tl;dr: Собрал инструмент, который делает AI реально надёжным. 120+ моделей, 9 стадий, слепой peer review, adversarial атаки, проверка фактов по живому вебу. Не очередная обёртка. Пайплайн уничтожения галлюцинаций. И отзывы сносят крышу.

Для твоей аудитории это может быть понятная тема: главная проблема AI сейчас в том, что он соглашается с тобой, даже когда врёт. Triall решает это просто. Три модели отвечают независимо, потом вслепую проверяют друг друга. Adversarial refinement, проверка фактов по вебу, devil's advocate. Одна модель промахнётся, другие поймают.

Бесплатная подписка, если хочешь попробовать. Я Маартен, соло-дев из Голландии.

https://triall.ai?lng=ru&utm_source=telegram&utm_medium=outreach&utm_campaign=misha_davai_po_novoi""", "ru"))

# 10. @tochkinadai (14.3K subs, "Точки над ИИ", casual, admin @hello_voic)
messages.append(("tochkinadai", """Привет! «Точки над ИИ» один из тех каналов, где AI рассматривают с позиции реального бизнеса, а не хайпа. Внедрение AI в бизнес-процессы реально важная тема.

tl;dr: Собрал инструмент, который делает AI реально надёжным. 120+ моделей, 9 стадий, слепой peer review, adversarial атаки, проверка фактов по живому вебу. Не очередная обёртка. Пайплайн уничтожения галлюцинаций. И отзывы сносят крышу.

Для бизнеса доверие к AI-ответам критично. Triall решает это: три модели из 120+ отвечают независимо, вслепую рецензируют друг друга. Adversarial refinement, проверка фактов по живому вебу, devil's advocate. Разные данные обучения = разные ошибки. Система ловит то, что одна модель пропустит.

Бесплатная подписка, если интересно потестить. Я Маартен, соло-разработчик из Голландии.

https://triall.ai?lng=ru&utm_source=telegram&utm_medium=outreach&utm_campaign=tochkinadai""", "ru"))

# 11. @castalia_ai (13.7K subs, "Castalia", casual, admin @sanior1231)
messages.append(("castalia_ai", """Привет! Канал Castalia нравится, особенно подход к AI-инструментам вроде YTscribe. Видно, что разбираетесь в теме и выбираете реально полезные штуки.

tl;dr: Собрал инструмент, который делает AI реально надёжным. 120+ моделей, 9 стадий, слепой peer review, adversarial атаки, проверка фактов по живому вебу. Не очередная обёртка. Пайплайн уничтожения галлюцинаций. И отзывы сносят крышу.

Triall в формат канала вписался бы отлично: не очередной чат-бот, а 9-стадийный пайплайн. Три модели из 120+ отвечают независимо, вслепую рецензируют друг друга, потом adversarial refinement, проверка фактов по вебу. Когда все три уверенно соглашаются без доказательств, система это флагает. Уверенный консенсус без пруфов опаснее явного бреда.

Бесплатная подписка, если хочешь потестить. Я Маартен, соло-разработчик из Голландии.

https://triall.ai?lng=ru&utm_source=telegram&utm_medium=outreach&utm_campaign=castalia_ai""", "ru"))

# 12. @tobeanmlspecialist (10.6K subs, "Стать специалистом по ML", casual, admin @kmsint)
messages.append(("tobeanmlspecialist", """Привет! Канал «Стать специалистом по ML» очень ценный, образовательный ML-контент на русском нужен и его мало кто делает на таком уровне.

tl;dr: Собрал инструмент, который делает AI реально надёжным. 120+ моделей, 9 стадий, слепой peer review, adversarial атаки, проверка фактов по живому вебу. Не очередная обёртка. Пайплайн уничтожения галлюцинаций. И отзывы сносят крышу.

Для ML-аудитории техническая суть будет понятна: разные архитектуры галлюцинируют по-разному (H-Neurons, Tsinghua, arXiv 2512.01797). Triall использует это. Три модели из 120+ отвечают независимо, слепой peer review, adversarial refinement, claim verification по вебу, devil's advocate. Не доверяешь одной модели, заставляешь их проверять друг друга.

Бесплатная подписка, если интересно. Я Маартен, соло-разработчик из Голландии.

https://triall.ai?lng=ru&utm_source=telegram&utm_medium=outreach&utm_campaign=tobeanmlspecialist""", "ru"))

# 13. @neuro_channel (10.1K subs, "Нейроканал", technical, admin @tproger_channels)
messages.append(("neuro_channel", """Привет! Нейроканал один из немногих, кто разбирает технические штуки вроде NVIDIA Nemotron и не скатывается в поверхностные новости. Качественный технический контент.

tl;dr: Собрал инструмент, который делает AI реально надёжным. 120+ моделей, 9 стадий, слепой peer review, adversarial атаки, проверка фактов по живому вебу. Не очередная обёртка. Пайплайн уничтожения галлюцинаций. И отзывы сносят крышу.

Для технической аудитории: core mechanism в том, что разные модели галлюцинируют из разных нейронов (H-Neurons paper, Tsinghua). Triall ставит три модели из 120+ отвечать независимо, потом слепой peer review. Adversarial refinement, проверка фактов по вебу, devil's advocate. Разные данные обучения = разные failure patterns.

Бесплатная подписка, если хочешь покопаться. Я Маартен, соло-разработчик из Голландии.

https://triall.ai?lng=ru&utm_source=telegram&utm_medium=outreach&utm_campaign=neuro_channel""", "ru"))

# 14. @dzenopulse (9K subs, "Тимур Угулава", casual, admin @timurugulava)
messages.append(("dzenopulse", """Привет, Тимур! Читаю канал, нравится подход к AI-маркетингу и длинные разборы. Мало кто делает такие лонгриды про AI с практической стороны.

tl;dr: Собрал инструмент, который делает AI реально надёжным. 120+ моделей, 9 стадий, слепой peer review, adversarial атаки, проверка фактов по живому вебу. Не очередная обёртка. Пайплайн уничтожения галлюцинаций. И отзывы сносят крышу.

Для маркетинга доверие к AI-ответам это всё. Если ты используешь AI для контента, а он уверенно врёт, репутация на кону. Triall решает это: три модели из 120+ отвечают независимо, вслепую рецензируют друг друга, потом adversarial refinement и проверка фактов по живому вебу. Разные данные обучения = разные ошибки.

Бесплатная подписка, если хочешь потестить. Я Маартен, соло-разработчик из Голландии, буду рад фидбеку.

https://triall.ai?lng=ru&utm_source=telegram&utm_medium=outreach&utm_campaign=dzenopulse""", "ru"))

# ============================================================================
# ENGLISH CHANNELS
# ============================================================================

# 15. @aipost (929K subs, "AI Post -- Artificial Intelligence", casual, admin @rational)
messages.append(("aipost", """Hey! AI Post is one of the biggest AI channels on Telegram and for good reason. The coverage on AI supply chain dynamics and chip smuggling was genuinely unique, nobody else covers that angle.

tl;dr: I built a tool that makes AI actually reliable. 120+ models, 9 stages, blind peer review, adversarial attacks, live fact-checking. Not another wrapper. A hallucination elimination pipeline. And the reviews have been kind of crazy.

Here's how it works: you pick any three models from 120+ across 8 families (Anthropic, OpenAI, Google, xAI, Meta, Mistral, DeepSeek, Qwen). They answer independently, then blindly peer-review each other. The surviving answer goes through adversarial refinement, live web claim verification, and a devil's advocate that tries to destroy whatever's left.

Different training data means different failure patterns. That's the actual mechanism.

Free subscription if you want to try it. I'm Maarten, solo dev from Holland.

https://triall.ai?lng=en&utm_source=telegram&utm_medium=outreach&utm_campaign=aipost""", "en"))

# 16. @hiaimediaen (528K subs, "Hi, AI - Tech News", technical, admin @anveklichNews)
messages.append(("hiaimediaen", """Hey! Hi AI's English channel is seriously impressive. The technical breakdowns on AI video generation and physics simulation are top tier, especially at that scale.

tl;dr: I built a tool that makes AI actually reliable. 120+ models, 9 stages, blind peer review, adversarial attacks, live fact-checking. Not another wrapper. A hallucination elimination pipeline. And the reviews have been kind of crazy.

The core idea: you pick any three models from 120+ across 8 families. Different training data, different blind spots. They answer independently, then blindly rip each other's work apart. Adversarial refinement, live web fact-checking, devil's advocate. The system even flags when all three confidently agree without evidence, because that's the most dangerous hallucination.

Free subscription if you want to check it out. I'm Maarten, solo dev from Holland.

https://triall.ai?lng=en&utm_source=telegram&utm_medium=outreach&utm_campaign=hiaimediaen""", "en"))

# 17. @neuralpony (220K subs, "Neural Pony", casual, admin @neuralforumInfo)
messages.append(("neuralpony", """Hey! Neural Pony is one of my go-to channels for AI art. That VEO3 ink-in-water logo piece was beautiful, you consistently find the most creative AI gen content out there.

tl;dr: I built a tool that makes AI actually reliable. 120+ models, 9 stages, blind peer review, adversarial attacks, live fact-checking. Not another wrapper. A hallucination elimination pipeline. And the reviews have been kind of crazy.

AI image gen is incredible, but when you need accurate answers, one model alone will confidently lie to your face. Triall fixes that: three models from 120+ answer independently, then blindly peer-review each other. Adversarial refinement, live web fact-checking, devil's advocate. Different architectures = different failure modes = reliable output.

Free sub if you want to try it. I'm Maarten, solo dev from Holland.

https://triall.ai?lng=en&utm_source=telegram&utm_medium=outreach&utm_campaign=neuralpony""", "en"))

# 18. @best_ai_tools (156K subs, "AI Tools", casual)
messages.append(("best_ai_tools", """Hey! AI Tools is one of the best curated channels out there. Wispr Flow and the other practical tool picks are always spot on. You clearly know what's actually useful vs. hype.

tl;dr: I built a tool that makes AI actually reliable. 120+ models, 9 stages, blind peer review, adversarial attacks, live fact-checking. Not another wrapper. A hallucination elimination pipeline. And the reviews have been kind of crazy.

For a tool-focused channel, Triall might be an interesting one to cover: it's not a chatbot, it's a pipeline. You pick three models from 120+ across 8 families. They answer independently, blindly peer-review each other, then the surviving answer goes through adversarial refinement, live web claim verification, and a devil's advocate. When all three confidently agree without evidence, the system catches it.

Free subscription if you want to test it. I'm Maarten, solo dev from Holland.

https://triall.ai?lng=en&utm_source=telegram&utm_medium=outreach&utm_campaign=best_ai_tools""", "en"))

# 19. @artificial_intelligence_com (68.8K subs, "Artificial Intelligence", casual)
messages.append(("artificial_intelligence_com", """Hey! Your channel has a nice mix of practical ML content. The Python tutorials with k-Means clustering and hands-on ML projects are exactly what people need.

tl;dr: I built a tool that makes AI actually reliable. 120+ models, 9 stages, blind peer review, adversarial attacks, live fact-checking. Not another wrapper. A hallucination elimination pipeline. And the reviews have been kind of crazy.

If you're teaching people ML with Python, you know how models fail in different ways. Triall uses that exact principle: three models from 120+ answer independently, then blindly peer-review each other. Adversarial refinement, live web fact-checking, devil's advocate. Different training data = different failure patterns. The system catches what one model misses.

Free subscription if you want to check it out. I'm Maarten, solo dev from Holland.

https://triall.ai?lng=en&utm_source=telegram&utm_medium=outreach&utm_campaign=artificial_intelligence_com""", "en"))

# 20. @codeprogrammer (68.1K subs, "Machine Learning with Python", technical, admin @HusseinSheikho)
messages.append(("codeprogrammer", """Hey Hussein! Machine Learning with Python is a solid channel, the ML tutorials and Python code examples are really well structured. Clean, practical, no fluff.

tl;dr: I built a tool that makes AI actually reliable. 120+ models, 9 stages, blind peer review, adversarial attacks, live fact-checking. Not another wrapper. A hallucination elimination pipeline. And the reviews have been kind of crazy.

As someone who teaches ML, you'll appreciate the technical core: different architectures hallucinate from different neurons (H-Neurons paper, Tsinghua, arXiv 2512.01797). Triall exploits this. Three models from 120+ answer independently, blind peer review, adversarial refinement, live web claim verification, devil's advocate. Instead of trusting one model, you make them verify each other.

Free subscription if you want to dig into it. I'm Maarten, solo dev from Holland.

https://triall.ai?lng=en&utm_source=telegram&utm_medium=outreach&utm_campaign=codeprogrammer""", "en"))

# 21. @generativeai_gpt (28.4K subs, "Generative AI", technical, admin @coderfunBuy)
messages.append(("generativeai_gpt", """Hey! Generative AI is a great channel, especially the GenAI interview prep content. Practical questions and technical depth in the same place is hard to find.

tl;dr: I built a tool that makes AI actually reliable. 120+ models, 9 stages, blind peer review, adversarial attacks, live fact-checking. Not another wrapper. A hallucination elimination pipeline. And the reviews have been kind of crazy.

Speaking of interview questions: "How do you make AI reliable?" has one answer now. Three models from 120+ answer independently, blind peer review, adversarial refinement, live web fact-checking, devil's advocate. Different training data means different hallucination patterns. Make models compete instead of trusting one. That's the mechanism behind Triall.

Free subscription if you want to try it. I'm Maarten, solo dev from Holland.

https://triall.ai?lng=en&utm_source=telegram&utm_medium=outreach&utm_campaign=generativeai_gpt""", "en"))

# 22. @gpt_anthropic (27.8K subs, "OpenAI | ChatGPT | GPT-4o", technical)
messages.append(("gpt_anthropic", """Hey! Good channel, always on top of the latest OpenAI and Anthropic news. The GPT-5.4 Mini and Nano coverage was right on time.

tl;dr: I built a tool that makes AI actually reliable. 120+ models, 9 stages, blind peer review, adversarial attacks, live fact-checking. Not another wrapper. A hallucination elimination pipeline. And the reviews have been kind of crazy.

You cover all the big model families, so this should resonate: instead of picking one model and hoping it's right, Triall lets you pick any three from 120+ across Anthropic, OpenAI, Google, xAI, Meta, Mistral, DeepSeek, Qwen. They answer independently, blindly peer-review each other. Adversarial refinement, live web claim verification, devil's advocate. Different training data = different blind spots = reliable output.

Free sub if you want to try it. I'm Maarten, solo dev from Holland.

https://triall.ai?lng=en&utm_source=telegram&utm_medium=outreach&utm_campaign=gpt_anthropic""", "en"))

# 23. @deeplearning005 (9.8K subs, "AI & Deep Learning", casual)
messages.append(("deeplearning005", """Hey! AI & Deep Learning is a solid channel, consistent curation of AI tools and research. Good signal-to-noise ratio.

tl;dr: I built a tool that makes AI actually reliable. 120+ models, 9 stages, blind peer review, adversarial attacks, live fact-checking. Not another wrapper. A hallucination elimination pipeline. And the reviews have been kind of crazy.

Here's the core idea: you pick any three models from 120+ across 8 families. Different architectures, different blind spots. They answer independently, then blindly rip each other's work apart. The surviving answer goes through adversarial refinement, live web fact-checking, and a devil's advocate. The system flags when all three agree without evidence, that's actually the most dangerous hallucination.

Free subscription if you want to check it out. I'm Maarten, solo dev from Holland.

https://triall.ai?lng=en&utm_source=telegram&utm_medium=outreach&utm_campaign=deeplearning005""", "en"))

# 24. @aiplusme (8.9K subs, "Ai+Me -- Artificial Intelligence", casual)
messages.append(("aiplusme", """Hey! Ai+Me is a cool channel, the mix of Sam Altman commentary and open source AI coverage is refreshing. You clearly think about where this is all heading.

tl;dr: I built a tool that makes AI actually reliable. 120+ models, 9 stages, blind peer review, adversarial attacks, live fact-checking. Not another wrapper. A hallucination elimination pipeline. And the reviews have been kind of crazy.

Altman talks about making AI better, but every single-model tool has the same problem: it agrees with you even when it's wrong. Triall fixes that. Three models from 120+ answer independently, blindly peer-review each other. Adversarial refinement, live web fact-checking, devil's advocate. Different training data means different failure patterns. Make them compete, don't trust one alone.

Free sub if you want to try it. I'm Maarten, solo dev from Holland.

https://triall.ai?lng=en&utm_source=telegram&utm_medium=outreach&utm_campaign=aiplusme""", "en"))

# 25. @chatgptmastermind (6.2K subs, "The Prompt Index", technical)
messages.append(("chatgptmastermind", """Hey! The Prompt Index is exactly the kind of channel the prompt engineering crowd needs. Focused, technical, no fluff.

tl;dr: I built a tool that makes AI actually reliable. 120+ models, 9 stages, blind peer review, adversarial attacks, live fact-checking. Not another wrapper. A hallucination elimination pipeline. And the reviews have been kind of crazy.

Here's the thing about prompt engineering: even the best prompt can't fix a model hallucinating. Triall takes a different approach entirely. Three models from 120+ answer independently, blind peer review, adversarial refinement, live web fact-checking, devil's advocate. The prompt matters, but making models verify each other matters more. Different training data = different failure patterns.

Free subscription if you want to see how it handles your best prompts. I'm Maarten, solo dev from Holland.

https://triall.ai?lng=en&utm_source=telegram&utm_medium=outreach&utm_campaign=chatgptmastermind""", "en"))

# 26. @brainstorm_ai (4.1K subs, "Brain Storm | AI", casual, admin @Vldsdma)
messages.append(("brainstorm_ai", """Hey! Brain Storm is a great find. The post about that Google engineer's AI agent framework was interesting, you clearly dig deeper than surface-level AI news.

tl;dr: I built a tool that makes AI actually reliable. 120+ models, 9 stages, blind peer review, adversarial attacks, live fact-checking. Not another wrapper. A hallucination elimination pipeline. And the reviews have been kind of crazy.

Since you cover AI agents and frameworks: Triall is essentially an adversarial multi-agent system for reliability. Three models from 120+ answer independently, blind peer review, adversarial refinement, live web claim verification, devil's advocate. Different architectures = different blind spots. Instead of one agent trusting itself, multiple agents verify each other.

Free subscription if you want to try it. I'm Maarten, solo dev from Holland.

https://triall.ai?lng=en&utm_source=telegram&utm_medium=outreach&utm_campaign=brainstorm_ai""", "en"))

# ============================================================================
# TURKISH
# ============================================================================

# 27. @yapayarsiv (1.6K subs, "Yapay Zeka Arsivi", casual, admin @PyLeo)
messages.append(("yapayarsiv", """Selam! Yapay Zeka Arsivi'ni takip ediyorum, AI illustrasyon ve gorsel icerikler konusunda Turkce kanal bulmak cok zor. Imagen AI icerigi guzeldi.

tl;dr: AI'yi gercekten guvenilir yapan bir arac gelistirdim. 120+ model, 9 asama, kor peer review, adversarial ataklar, canli web uzerinden fact-checking. Bir wrapper daha degil. Halusinasyon yok etme pipeline'i. Ve gelen yorumlar inanilmaz.

Nasil calisiyor: 120+ modelden uc tanesini seciyorsun (Anthropic, OpenAI, Google, xAI, Meta, Mistral, DeepSeek, Qwen). Bagimsiz cevap veriyorlar, sonra birbirlerini kor sekilde inceliyorlar. Adversarial refinement, canli web uzerinden fact-checking, devil's advocate. Farkli egitim verisi = farkli hatalar. Birinin kacirdigi hatalarini digerlerinin yakalamasi.

Denemek istersen ucretsiz abonelik. Ben Maarten, Hollanda'dan solo gelistiriciyim.

https://triall.ai?lng=tr&utm_source=telegram&utm_medium=outreach&utm_campaign=yapayarsiv""", "tr"))

# ============================================================================
# CHINESE
# ============================================================================

# 28. @ai_copilot_channel (8.5K subs, "AI Copilot", casual, admin @cnpcmx)
messages.append(("ai_copilot_channel", """你好！AI Copilot 频道很赞，Gemini 3.1 Flash Lite 的内容和各种AI工具的中文介绍非常实用，这样的中文AI频道很难找到。

tl;dr: 我做了一个让AI真正可靠的工具。120+模型，9个阶段，盲审peer review，对抗性攻击，实时网页事实核查。不是又一个wrapper。是一个消除幻觉的pipeline。用户反馈非常疯狂。

工作原理：从120+模型中选三个（Anthropic、OpenAI、Google、xAI、Meta、Mistral、DeepSeek、Qwen）。它们独立回答，然后盲审互相检查。接着经过对抗性优化、实时网页事实核查和devil's advocate。不同训练数据意味着不同的错误模式，一个模型漏掉的，其他模型能抓住。

想试试的话，免费订阅送你。我是Maarten，来自荷兰的独立开发者。

https://triall.ai?lng=zh&utm_source=telegram&utm_medium=outreach&utm_campaign=ai_copilot_channel""", "zh"))


# ============================================================================
# INSERT ALL MESSAGES
# ============================================================================

count = 0
for username, text, lang in messages:
    try:
        db.insert_message(username, text, lang)
        count += 1
        print(f"[{count}] Inserted message for @{username} ({lang})")
    except Exception as e:
        print(f"ERROR for @{username}: {e}")

print(f"\nTotal messages saved: {count}")
