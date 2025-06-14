import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import os

def create_sleep_visualizations(df: pd.DataFrame) -> tuple[str, str]:
    # Создаем директорию для графиков, если её нет
    os.makedirs('plots', exist_ok=True)
    
    # Генерируем уникальные имена файлов с временной меткой
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plot1_path = f'plots/sleep_duration_{timestamp}.png'
    plot2_path = f'plots/sleep_trend_{timestamp}.png'
    
    # 1. Столбчатая диаграмма распределения продолжительности сна
    plt.figure(figsize=(10, 6))
    # Создаем интервалы для продолжительности сна
    bins = [0, 4, 6, 8, 10, 12]
    labels = ['<4ч', '4-6ч', '6-8ч', '8-10ч', '>10ч']
    df['sleep_category'] = pd.cut(df['sleep_hours'], bins=bins, labels=labels)
    
    # Строим столбчатую диаграмму
    sleep_counts = df['sleep_category'].value_counts().sort_index()
    sns.barplot(x=sleep_counts.index, y=sleep_counts.values)
    plt.title('Распределение продолжительности сна')
    plt.xlabel('Продолжительность сна')
    plt.ylabel('Количество дней')
    plt.xticks(rotation=45)
    
    # Добавляем значения над столбцами
    for i, v in enumerate(sleep_counts.values):
        plt.text(i, v, str(v), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(plot1_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Линейный график тренда сна и самочувствия
    plt.figure(figsize=(12, 6))
    
    # Создаем индекс дат для графика
    df['date'] = pd.date_range(end=pd.Timestamp.now(), periods=len(df))
    
    # Создаем два графика на одной оси
    ax1 = plt.gca()
    ax2 = ax1.twinx()
    
    # График продолжительности сна
    ax1.plot(df['date'], df['sleep_hours'], 'b-', label='Продолжительность сна', linewidth=2)
    ax1.set_ylabel('Часы сна', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    
    # График самочувствия
    ax2.plot(df['date'], df['feeling_score'], 'r-', label='Самочувствие', linewidth=2)
    ax2.set_ylabel('Самочувствие (1-10)', color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    
    # Настройка графика
    plt.title('Тренд продолжительности сна и самочувствия')
    plt.xlabel('Дата')
    
    # Добавляем легенду
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    # Поворачиваем метки дат для лучшей читаемости
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(plot2_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return plot1_path, plot2_path 