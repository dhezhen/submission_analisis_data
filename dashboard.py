import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from matplotlib.font_manager import FontProperties  
import calendar
sns.set_theme(style='dark')

st.title('📊 Dashboard Analisis Bike Sharing')
with st.sidebar:
    st.title(' 📊 Dashboard Bike Sharing')
    st.image('https://upload.wikimedia.org/wikipedia/commons/c/c7/Zotwheelsbikeshare.jpg')


# Load data  
    day_data = pd.read_csv('bsDay_cleaned.csv')  
    hour_data = pd.read_csv('bsHour_cleaned.csv')  


    # Konversi kolom tanggal  
    day_data['date'] = pd.to_datetime(day_data['date'])  
    hour_data['date'] = pd.to_datetime(hour_data['date'])  



    # Ekstrak tahun dan bulan  
    day_data['year'] = day_data['date'].dt.year  
    day_data['month'] = day_data['date'].dt.month_name()  
    hour_data['year'] = hour_data['date'].dt.year  
    hour_data['month'] = hour_data['date'].dt.month_name()  



    # Filter tahun  
    selected_year = st.selectbox(  
            'Pilih Tahun',  
            ['Semua'] + sorted(day_data['year'].unique().tolist())  
        )  
        
        # Filter bulan  
    selected_month = st.selectbox(  
            'Pilih Bulan',  
            ['Semua'] + list(calendar.month_name)[1:]  
        )
    # Fungsi filter data  
    def filter_data(df):  
        filtered = df.copy()  
        if selected_year != 'Semua':  
            filtered = filtered[filtered['year'] == selected_year]  
        if selected_month != 'Semua':  
            filtered = filtered[filtered['month'] == selected_month]  
        return filtered    

    # Terapkan filter  
    filtered_day = filter_data(day_data)  
    filtered_hour = filter_data(hour_data)  

# Header status filter  
st.title('📈 Analisis Data Bike Sharing')  
st.markdown(f"""  
**Filter Aktif:**  
🗓️ Tahun: {selected_year}  
📅 Bulan: {selected_month}  
🔢 Jumlah Data: {len(filtered_day)} hari (dari dataset harian)  
🔢 Jumlah Data: {len(filtered_hour)} jam (dari dataset per jam)  
""")  

# # Function untuk menampilkan data  
# def display_data(df, data_name):  
#     st.header(f"Data {data_name} ")  
#     st.write(df.head())  
#     st.write(df.describe())  

# Menampilkan dataset  
# display_data(day_data, "Harian")  
# display_data(hour_data, "Per Jam")  



def plot_hourly_analysis(data):  
    try:  
        # Hitung total penyewaan per jam  
        hourly_data = data.groupby('hour', as_index=False)['count'].sum()  
        hourly_data = hourly_data.sort_values('count', ascending=True)  

        # Buat visualisasi  
        fig, ax = plt.subplots(figsize=(10, 6))  
        
        # Gunakan color gradient untuk highlight jam sibuk  
        palette = sns.color_palette("Blues_d", n_colors=len(hourly_data))  
        
        sns.barplot(  
            x='hour',  
            y='count',  
            data=hourly_data,  
            order=hourly_data['hour'],  
            palette=palette,  
            ax=ax  
        )   
 
        # Styling  
        ax.set_title('Distribusi Penyewaan per Jam (Tertinggi ke Terendah)', fontsize=16, pad=20)  
        ax.set_xlabel('Jam dalam Sehari', fontsize=12)  
        ax.set_ylabel('Total Penyewaan', fontsize=12)  
        ax.grid(axis='y', alpha=0.3)  
         
        # Format angka dengan separator  
        ax.yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))  
        
        # Rotasi label jam  
        plt.xticks(rotation=45)  
        
        # Tambahkan garis nilai di setiap bar  
        for p in ax.patches:  
            ax.annotate(  
                f'{p.get_height():,.0f}',   
                (p.get_x() + p.get_width() / 2., p.get_height()),  
                ha='center',   
                va='center',   
                xytext=(0, 7),   
                textcoords='offset points',  
                rotation=45  
            )  

        st.pyplot(fig)  
        
        # Tambahkan tabel data  
        st.subheader("Detail Jumlah Penyewaan per Jam")  
        
        # Format angka dan urutkan kolom  
        formatted_data = hourly_data.copy()  
        formatted_data['Total Penyewaan'] = formatted_data['count'].apply(lambda x: f"{x:,.0f}")  
        formatted_data = formatted_data[['hour', 'Total Penyewaan']]  
        formatted_data.columns = ['Jam', 'Total Penyewaan']  

        # Tampilkan tabel dengan container width penuh  
        st.table(formatted_data)  
        
    except Exception as e:  
        st.error(f"Error dalam plot hourly: {str(e)}")  
        st.write("Data sample:", data[['hour', 'count']].head(3) if 'hour' in data.columns else "Kolom 'hour' tidak ada")  
# Panggil fungsi dengan data hourly  
# st.divider()  
# st.header("📊 Analisis Per Jam")  
# plot_hourly_analysis(hour_data)  


# Function plot musiman  
def plot_seasonal_rentals(data):  
    # Mapping musim  
    season_map = {  
        1: 'Winter',   
        2: 'Spring',   
        3: 'Summer',   
        4: 'Fall'  
    }  
    
    # Membuat DataFrame baru untuk menghindari modifikasi data asli  
    plot_data = data[['season', 'count']].copy()  
    plot_data['season_name'] = plot_data['season'].map(season_map)  
    
    # Grouping dengan aggregasi yang lebih eksplisit  
    rentals_by_season = plot_data.groupby('season_name', as_index=False)['count'].mean()  
    
    # Membuat plot dengan matplotlib langsung  
    fig, ax = plt.subplots(figsize=(10, 5))  
    
    ax.bar(  
        x=rentals_by_season['season_name'],  
        height=rentals_by_season['count'],  
        color=['#4CAF50', '#2196F3', '#FFC107', '#9C27B0']  
    )  
    
    ax.set_title("Rata-rata Penyewaan per Musim", fontsize=14)  
    ax.set_xlabel("Musim", fontsize=12)  
    ax.set_ylabel("Rata-rata Penyewaan", fontsize=12)  
    ax.grid(axis='y', alpha=0.3)  
    
    st.pyplot(fig)

def plot_weather_analysis(data):  
    try:  
        # Hitung rata-rata penyewaan per kondisi cuaca  
        weather_rentals = data.groupby('weather_condition')['count'].mean().sort_values(ascending=False)  
        
        # Buat figure matplotlib  
        fig, ax = plt.subplots(figsize=(10, 6))  
        
        # Generate warna custom  
        colors = ['#B3E5FC' if (x != weather_rentals.max()) else '#01579B' for x in weather_rentals.values]  
        
        # Buat plot menggunakan seaborn  
        sns.barplot(  
            x=weather_rentals.index,  
            y=weather_rentals.values,  
            palette=colors,  
            ax=ax  
        )  
        
        # Atur styling  
        ax.set_title('Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca', fontsize=14, pad=20)  
        ax.set_xlabel('Kondisi Cuaca', fontsize=12)  
        ax.set_ylabel('Rata-rata Penyewaan', fontsize=12)  
        ax.tick_params(axis='x', rotation=45)  
        
        # Highlight bar tertinggi  
        max_bar = ax.patches[0]  
        max_bar.set_edgecolor('#FF5722')  
        max_bar.set_linewidth(2)  
        
        # Tampilkan grafik di Streamlit  
        st.pyplot(fig)  
        
        # Tambahkan tabel data  
        st.subheader("Detail Rata-rata per Kondisi Cuaca")  
        
        # Format data untuk tabel  
        table_data = pd.DataFrame({  
            'Kondisi Cuaca': weather_rentals.index,  
            'Rata-rata Penyewaan': weather_rentals.values.round(1)  
        })  
        
        # Format angka dengan separator  
        table_data['Rata-rata Penyewaan'] = table_data['Rata-rata Penyewaan'].apply(lambda x: f"{x:,.1f}")  
        
        # Tampilkan tabel  
        st.table(table_data[['Kondisi Cuaca', 'Rata-rata Penyewaan']])  
        
    except Exception as e:  
        st.error(f"Error dalam analisis cuaca: {str(e)}")  
        st.write("Data sample:", data[['weather_condition', 'count']].head(3) if 'weather_condition' in data.columns   
                 else "Kolom 'weather_condition' tidak ditemukan")  
# Panggil fungsi dalam aplikasi Streamlit  
# plot_weather_analysis(day_data)  

def plot_seasonal_analysis(data):  
    # Hitung metrik  
    season_rentals = data.groupby('season')['count'].mean().sort_values(ascending=False)  
    total_rentals_per_season = data.groupby('season')['count'].sum().sort_values(ascending=False)  
    
    # Mapping nama musim  
    season_names = {  
        1: 'Winter ❄️',  
        2: 'Spring 🌸',  
        3: 'Summer ☀️',  
        4: 'Fall 🍂'  
    }  
    
    # Buat DataFrame hasil analisis  
    season_summary = pd.DataFrame({  
        'Rata-rata Penyewaan': season_rentals,  
        'Total Penyewaan': total_rentals_per_season  
    }).rename(index=season_names)  
    
    # Buat visualisasi  
    fig, ax = plt.subplots(figsize=(10, 6))  
    
    # Plot batang untuk rata-rata  
    sns.barplot(  
        x=season_summary.index,  
        y='Rata-rata Penyewaan',  
        data=season_summary,  
        palette='viridis',  
        ax=ax  
    )  
    
    # Tambahkan label nilai  
    for p in ax.patches:  
        ax.annotate(  
            f'{p.get_height():.0f}',  
            (p.get_x() + p.get_width()/2., p.get_height()),  
            ha='center',   
            va='center',   
            xytext=(0, 10),   
            textcoords='offset points',  
            fontsize=10,  
            color='black'  
        )  
    
    # Atur tampilan  
    ax.set_title('Analisis Penyewaan per Musim', fontsize=16, pad=20)  
    ax.set_xlabel('Musim', fontsize=12)  
    ax.set_ylabel('Rata-rata Penyewaan', fontsize=12)  
    ax.grid(axis='y', alpha=0.3)  
    
    # Tampilkan tabel total penyewaan  
    st.pyplot(fig)  
    
    # Tampilkan tabel pendukung  
    st.subheader("Detail Total Penyewaan per Musim")  
    season_summary['Total Penyewaan'] = season_summary['Total Penyewaan'].apply(lambda x: f"{x:,}")  
    st.dataframe(  
        season_summary[['Total Penyewaan']],  
        column_config={  
            "Total Penyewaan": st.column_config.NumberColumn(  
                format="%d 🚴"  
            )  
        },  
        use_container_width=True  
    )  

# Panggil fungsi di aplikasi Streamlit  
# plot_seasonal_analysis(day_data)  

def plot_workingday_analysis(data):  
    # Hitung persentase dan total hari  
    workingday_percentages = data.groupby('is_workingday')['count'].sum() / data['count'].sum() * 100  
    workingday_totals = data.groupby('is_workingday')['count'].count()  
    
    # Buat label dengan format  
    labels = [  
        f'Tidak Bekerja ({workingday_totals.get(0, 0):,} hari)',   
        f'Bekerja ({workingday_totals.get(1, 0):,} hari)'  
    ]  
    
    # Warna dan styling  
    colors = ['#4CAF50', '#2196F3']  
    explode = (0.05, 0)  # Sedikit highlight untuk bagian pertama  
    
    # Buat visualisasi  
    fig, ax = plt.subplots(figsize=(8, 8))  
    
    wedges, texts, autotexts = ax.pie(  
        workingday_percentages,  
        explode=explode,  
        colors=colors,  
        autopct='%1.1f%%',  
        startangle=90,  
        textprops={'fontsize': 12}  
    )  
    
    # Atur tampilan  
    ax.set_title(' Distribusi Penyewaan Berdasarkan Hari Kerja', fontsize=16, pad=20)  
    ax.legend(  
        wedges,  
        labels,  
        title="Kategori Hari",  
        loc="upper left",  
        bbox_to_anchor=(1, 0.9)  
    )  
    
    # Perbesar persentase di chart  
    for autotext in autotexts:  
        autotext.set_fontsize(14)  
        autotext.set_color('white')  
    
    # Tampilkan di Streamlit  
    st.pyplot(fig)  

# Panggil fungsi di aplikasi  
# plot_workingday_analysis(day_data)

# --- Layout Utama ---  

# --- Analisis Pendukung di Bawah ---  
st.divider()  
tab1, tab2,tab3,tab4= st.tabs(["Pola Hari Kerja","Peyewa Berdasarkan Jam","Kondisi Cuaca", "Kondisi musim"
])  

# with tab1:  
#     display_data(day_data, "Harian")  
#     display_data(hour_data, "Per Jam")  

with tab1:
    plot_workingday_analysis(filtered_day) 
with tab2:  
 plot_hourly_analysis(filtered_hour)  
#  plot_histogram(day_data, 'temperature', "Distribusi Temperatur Harian")  
with tab3: 
    plot_weather_analysis(filtered_day) 
with tab4: 
    plot_seasonal_analysis(filtered_day) 

    

