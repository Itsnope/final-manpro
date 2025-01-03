# -*- coding: utf-8 -*-
"""22220027-Noverianus-Prak Manajemen Proyek.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Cbu7vC1vP-hTgnAenQNI1HHGvTZFIYLi

# Mount Google Drive
"""

from google.colab import drive
drive.mount('/content/drive')

"""# Import library dan dataset"""

# Import library
import re, nltk
import numpy as np
import pandas as pd
import seaborn as sns
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from matplotlib import pyplot as plt
from nltk.tokenize import word_tokenize
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, SpatialDropout1D, Bidirectional


nltk.download('vader_lexicon')
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('stopwords')

# Membaca dataset
df = pd.read_csv('/content/drive/MyDrive/dataset_devin/Devin ai youtube comments.csv')

# Melihat isi dataset
df

# Mengambil kolom text
df = df[['text']]
df

"""# Pre-Processing

## Data Cleansing
"""

# Menghapus data terduplikasi dan Null/NaN
df = df.drop_duplicates(subset=['text'])
df = df.dropna()

# Mengecek data terduplikasi dan NaN
print("Data terduplikasi :", df.duplicated().sum())
print("Data Null/NaN :")
df.isnull().sum()

# Fungsi untuk membersihkan teks komentar YouTube
def clean_youtube_comment(text):
    # Menghapus mention (@username) dari teks
    text = re.sub(r'@[A-Za-z0-9_]+', '', text)
    # Menghapus hashtag (#hashtag) dari teks
    text = re.sub(r'#\w+', '', text)
    # Menghapus URL (tautan mulai dengan http atau https)
    text = re.sub(r'https?://\S+', '', text)
    # Menghapus karakter non-alfanumerik kecuali spasi, tanda baca ringan, dan emoji
    text = re.sub(r'[^A-Za-z0-9 .,!?]', '', text)
    # Mengganti beberapa spasi berturut-turut dengan satu spasi dan menghapus spasi di awal/akhir teks
    text = re.sub(r'\s+', ' ', text).strip()
    # Additional cleaning steps
    text = re.sub(r'[^\w\s.,!?]', '', text)  # Keep only words, spaces, and basic punctuation
    text = re.sub(r'\s+', ' ', text)  # Normalize spaces
    text = re.sub(r'\.+', '.', text)  # Normalize periods
    text = re.sub(r'\!+', '!', text)  # Normalize exclamation marks
    text = re.sub(r'\?+', '?', text)  # Normalize question marks
    # Mengembalikan teks yang sudah dibersihkan
    return text

# Menerapkan fungsi clean_youtube_comment pada kolom 'comment' di dataframe df
df['text'] = df['text'].apply(clean_youtube_comment)

# Melihat hasil data cleansing
df

"""## Normalisasi"""

# Mengubah data teks menjadi huruf kecil (lower)
df['text'] = df['text'].str.lower()

df

"""## Stopwords"""

# Inisialisasi stopwords
stop_words = set(stopwords.words('english'))

# Menghapus stopwords
df['text'] = df['text'].apply(lambda x: ' '.join([word for word in x.split() if word not in stop_words]))
df

# Mengecek data terduplikasi dan NaN setelah stopwords
print("Data terduplikasi :", df.duplicated().sum())
print("Data Null/NaN :")
df.isnull().sum()

# Menghapus data terduplikasi
df = df.drop_duplicates(subset=['text'])

print("Data terduplikasi :", df.duplicated().sum())

"""## Tokenisasi"""

# Tokenisasi
tokenized = df['text'].apply(lambda x:x.split())
tokenized

"""## Lemmatisasi"""

# Inisialisasi lemmatizer
lemmatizer = WordNetLemmatizer()

# Lemmatisasi
lemmatized = tokenized.apply(lambda tokens: [lemmatizer.lemmatize(token) for token in tokens])
print("Lemmatized Text:")
print(lemmatized)

# Gabungkan token menjadi string
df['text'] = lemmatized.apply(lambda x: ' '.join(x))

# Cek format data
print("\nContoh data setelah preprocessing:")
print(df.head())

# Simpan dalam format (string + label)
df.to_csv('/content/drive/MyDrive/dataset_devin/preprocess_Devin_ai_youtube_comments.csv', index=False)

"""## Labeling"""

data = pd.read_csv("/content/drive/MyDrive/dataset_devin/preprocess_Devin_ai_youtube_comments.csv", encoding='latin1')

# Menghapus data NaN
data = data.dropna()

data.isnull().sum()

# Memastikan kolom text berisi string, bukan float
data['text'] = data['text'].astype(str)

# Inisialisasi VADER
sid = SentimentIntensityAnalyzer()

# Fungsi untuk menentukan label sentimen berdasarkan compound score VADER
def get_sentiment_label(compound_score):
    if compound_score > 0.1:
        return 'Positif'
    elif compound_score < -0.1:
        return 'Negatif'
    else:
        return 'Netral'

# List untuk menyimpan hasil analisis
compound_scores = []
sentiments = []
total_positif = total_negatif = total_netral = 0

# Melakukan analisis sentimen untuk setiap komentar
for comment in data['text']:
    try:
        # Mendapatkan scores dari VADER
        scores = sid.polarity_scores(comment)

        # Menyimpan compound score
        compound_scores.append(scores['compound'])

        # Menentukan sentiment berdasarkan compound score
        sentiment = get_sentiment_label(scores['compound'])
        sentiments.append(sentiment)

        # Menghitung total untuk setiap kategori
        if sentiment == 'Positif':
            total_positif += 1
        elif sentiment == 'Negatif':
            total_negatif += 1
        else:
            total_netral += 1
    except Exception as e:
        print(f"Error processing comment: {comment}")
        print(f"Error message: {str(e)}")
        # Append neutral sentiment for error cases
        compound_scores.append(0)
        sentiments.append('Netral')
        total_netral += 1

# Menambahkan hasil analisis ke dataframe
data['compound_score'] = compound_scores
data['sentiment'] = sentiments

# Menampilkan hasil analisis
print(f'Hasil Analisis Data:\nPositif = {total_positif}\nNetral = {total_netral}\nNegatif = {total_negatif}')
print(f'Total Data : {len(data)}')

# Visualisasi distribusi sentimen
plt.figure(figsize=(10, 6))
data['sentiment'].value_counts().plot(kind='barh', color=sns.palettes.mpl_palette('Dark2'))
plt.title('Distribusi Sentimen menggunakan VADER')
plt.xlabel('Jumlah Komentar')
plt.ylabel('Sentimen')
plt.gca().spines[['top', 'right']].set_visible(False)
plt.show()

# Melihat contoh hasil analisis
print("\nContoh hasil analisis VADER:")
sample_results = data[['text', 'compound_score', 'sentiment']].head(10)
print(sample_results)

# Menyimpan hasil labeling
data.to_csv('/content/drive/MyDrive/dataset_devin/labeled_Devin_ai_youtube_comments.csv', index=False)

"""## Encoding label"""

data = pd.read_csv('/content/drive/MyDrive/dataset_devin/labeled_Devin_ai_youtube_comments.csv')
data

# Encode label sentimen ke numerik
label_encoder = LabelEncoder()
data['sentiment_encoded'] = label_encoder.fit_transform(data['sentiment'])  # 0 = Negatif, 1 = Netral, 2 = Positif

"""## Pemisahan fitur dan label"""

# Pisahkan data fitur (teks) dan label (sentimen)
X = data['text']
y = data['sentiment_encoded']

"""## Pembagian data train dan test

"""

from imblearn.over_sampling import SMOTE

# Terapkan SMOTE untuk menyeimbangkan kelas
smote = SMOTE(random_state=42)
X_balanced, y_balanced = smote.fit_resample(X_train_pad, y_train)

# Ubah label ke format kategorikal setelah SMOTE
y_balanced_cat = to_categorical(y_balanced, num_classes=3)

# Bagi data menjadi data latih dan data uji
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

"""## Tokenisasi teks & Padding sequence"""

# Tokenisasi dan padding teks
max_words = 5000  # Batas jumlah kata
max_len = 100     # Panjang maksimum teks yang akan dipakai

tokenizer = Tokenizer(num_words=max_words, oov_token="<OOV>")
tokenizer.fit_on_texts(X_train)
X_train_seq = tokenizer.texts_to_sequences(X_train)
X_test_seq = tokenizer.texts_to_sequences(X_test)
X_train_pad = pad_sequences(X_train_seq, maxlen=max_len, padding='post')
X_test_pad = pad_sequences(X_test_seq, maxlen=max_len, padding='post')

"""## Konversi label ke format kategorikal"""

# Ubah label menjadi kategori
y_train_cat = to_categorical(y_train, num_classes=3)
y_test_cat = to_categorical(y_test, num_classes=3)

"""# Membangun Model"""

data

# Mengambil kolom text
df = data[['text', 'sentiment', 'sentiment_encoded']]
df

from tensorflow.keras.regularizers import l2
from tensorflow.keras.layers import BatchNormalization

# Membangun model
model = Sequential()

# Layer Embedding untuk mengkonversi kata ke vector
model.add(Embedding(input_dim=max_words, output_dim=64, input_length=(max_len,), embeddings_regularizer=l2(1e-6)))

model.add(SpatialDropout1D(0.1))

# Layer LSTM pertama dengan return sequences
model.add(LSTM(64, return_sequences=True, dropout=0.1, recurrent_dropout=0.1))
model.add(BatchNormalization())

# Layer LSTM kedua
model.add(LSTM(32, return_sequences=True, dropout=0.1, recurrent_dropout=0.1))
model.add(BatchNormalization())

# Layer LSTM ketiga tanpa return sequences
model.add(LSTM(16, dropout=0.1, recurrent_dropout=0.1))
model.add(BatchNormalization())

# Dense layer dengan aktivasi relu
model.add(Dense(64, activation='relu', kernel_regularizer=l2(1e-6)))
model.add(BatchNormalization())
model.add(Dropout(0.2))

model.add(Dense(32, activation='relu', kernel_regularizer=l2(1e-6)))
model.add(BatchNormalization())

# Dropout untuk mencegah overfitting
model.add(Dropout(0.2))

# Output layer dengan 3 neuron (3 kelas sentimen) dan aktivasi softmax
model.add(Dense(3, activation='softmax'))

# Compile model
optimizer = Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-07)

model.compile(optimizer=optimizer,
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Tampilkan summary model
model.summary()

"""# Melatih model

## Callback untuk Early Stopping
"""

# Callback untuk Early Stopping
early_stopping = EarlyStopping(
    monitor='val_loss',      # Monitor validation loss
    patience=3,              # Number of epochs with no improvement after which training will stop
    mode='min',             # Training will stop when monitored value stops decreasing
    restore_best_weights=True,  # Restore model weights from the epoch with the best value of the monitored quantity
    verbose=1
)

"""## Callback untuk Model Checkpoint"""

# Callback untuk Model Checkpoint
checkpoint = ModelCheckpoint(
    'best_model.h5.keras',        # Path to save the model
    monitor='val_accuracy', # Monitor validation accuracy
    mode='max',            # Save when monitored value is maximum
    save_best_only=True,   # Only save the best model
    verbose=1
)

"""## Pelatihan Model"""

# Hitung class weight secara otomatis
from sklearn.utils.class_weight import compute_class_weight

class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_train),
    y=y_train
)

class_weights = dict(enumerate(class_weights))

# Latih model dengan class_weight
history = model.fit(
    X_train_pad,
    y_train_cat,
    epochs=20,
    batch_size=32,
    validation_split=0.2,
    class_weight=class_weights,  # Tambahkan class weights
    callbacks=[early_stopping, checkpoint],
    verbose=1
)

# Pelatihan Model
history = model.fit(
    X_train_pad,           # Training data
    y_train_cat,          # Training labels
    epochs=20,            # Maximum number of epochs
    batch_size=32,        # Batch size
    validation_split=0.2, # Use 20% of training data for validation
    callbacks=[early_stopping, checkpoint],  # Add callbacks
    class_weight=class_weights_dict,
    verbose=1
)

"""# Menguji model

## Evaluasi Model pada Data Uji
"""

# Evaluasi model pada data uji
test_loss, test_accuracy = model.evaluate(X_test_pad, y_test_cat, verbose=1)
print(f"Test Loss: {test_loss}")
print(f"Test Accuracy: {test_accuracy}")

"""## Prediksi pada Data Uji"""

# Prediksi sentimen pada data uji
predictions = model.predict(X_test_pad)
predicted_classes = np.argmax(predictions, axis=1)

# Decode label dari kategori ke bentuk aslinya
true_classes = np.argmax(y_test_cat, axis=1)

# Laporan klasifikasi
print("Classification Report:")
print(classification_report(true_classes, predicted_classes, target_names=label_encoder.classes_))

"""## Confusion Matrix"""

# Membuat confusion matrix
conf_matrix = confusion_matrix(true_classes, predicted_classes)

# Visualisasi confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.title("Confusion Matrix")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.show()

"""## Prediksi Komentar Baru"""

# Komentar baru untuk diuji
new_comments = [
    "This is amazing! I love it!",
    "I don't like this at all.",
    "It's okay, not bad but not great either."
]

# Preprocessing komentar baru
new_comments_seq = tokenizer.texts_to_sequences(new_comments)
new_comments_pad = pad_sequences(new_comments_seq, maxlen=max_len, padding='post')

# Prediksi
new_predictions = model.predict(new_comments_pad)
new_predicted_classes = np.argmax(new_predictions, axis=1)

# Decode prediksi
decoded_predictions = label_encoder.inverse_transform(new_predicted_classes)
for comment, sentiment in zip(new_comments, decoded_predictions):
    print(f"Comment: {comment}")
    print(f"Predicted Sentiment: {sentiment}")
    print("-" * 50)

import seaborn as sns

sns.countplot(data['sentiment'])
plt.title("Distribusi Sentimen")
plt.xlabel("Sentimen")
plt.ylabel("Jumlah")
plt.show()