import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Kalkulator & Visualisator Mekanika Teknik",
    page_icon="📐",
    layout="wide"
)

# --- HEADER APLIKASI ---
st.title("📐 Kalkulator & Visualisator Gaya Interaktif")
st.caption("🚀 **Created by : IrwanZanur@MekTek**")
st.write("Aplikasi untuk menghitung, memvisualisasikan, dan mengunduh laporan resultan gaya secara grafis maupun analitis.")

# --- SIDEBAR: METODE, SKALA, & INPUT GAYA ---
st.sidebar.header("⚙️ Pengaturan Simulasi")

# 1. Pilihan Metode Visualisasi
metode = st.sidebar.radio(
    "Pilih Metode Visualisasi:",
    ["Jajaran Genjang Bertingkat", "Poligon Gaya (Tip-to-Tail)"]
)

# 2. Input Skala Gaya
skala = st.sidebar.number_input("Skala Gaya (1 cm = ... kg)", min_value=1.0, value=100.0, step=10.0)

# Data Default
default_data = [
    {"Gaya": "P1", "Beban (kg)": 500.0, "Sudut (°)": 90.0},
    {"Gaya": "P2", "Beban (kg)": 400.0, "Sudut (°)": 45.0},
    {"Gaya": "P3", "Beban (kg)": 450.0, "Sudut (°)": 0.0},
    {"Gaya": "P4", "Beban (kg)": 550.0, "Sudut (°)": -40.0},
    {"Gaya": "P5", "Beban (kg)": 350.0, "Sudut (°)": 205.0},
]

st.sidebar.subheader("Tabel Input Gaya")
df_input = st.sidebar.data_editor(
    pd.DataFrame(default_data),
    num_rows="dynamic",
    use_container_width=True
)

st.sidebar.markdown("---")
st.sidebar.caption("👨‍💻 **Created by : IrwanZanur@MekTek**")

# --- PERHITUNGAN ANALITIS ---
if not df_input.empty:
    df_calc = df_input.copy()
    df_calc["Panjang (cm)"] = df_calc["Beban (kg)"] / skala
    
    # Konversi Sudut ke Radian
    rad = np.radians(df_calc["Sudut (°)"])
    
    # Komponen Sumbu X dan Y
    df_calc["Fx (kg)"] = df_calc["Beban (kg)"] * np.cos(rad)
    df_calc["Fy (kg)"] = df_calc["Beban (kg)"] * np.sin(rad)
    df_calc["Vx (cm)"] = df_calc["Panjang (cm)"] * np.cos(rad)
    df_calc["Vy (cm)"] = df_calc["Panjang (cm)"] * np.sin(rad)

    # Resultan Total
    Rx_kg = df_calc["Fx (kg)"].sum()
    Ry_kg = df_calc["Fy (kg)"].sum()
    R_total_kg = np.sqrt(Rx_kg**2 + Ry_kg**2)
    R_total_cm = R_total_kg / skala
    Sudut_R_deg = np.degrees(np.arctan2(Ry_kg, Rx_kg))

    # --- TAMPILAN RINGKASAN METRIK ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Resultan Gaya (R)", f"{R_total_kg:.2f} kg")
    col2.metric("Panjang Garis Resultan", f"{R_total_cm:.2f} cm")
    col3.metric("Arah / Sudut Resultan", f"{Sudut_R_deg:.2f}°")

    st.markdown("---")

    # --- GENERASI DIAGRAM MATPLOTLIB ---
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_aspect('equal')
    
    # Efek Kertas Milimeter (Grid Mayor & Minor)
    ax.minorticks_on()
    ax.grid(True, which='major', color='#b0bec5', linestyle='-', linewidth=0.8, alpha=0.7)
    ax.grid(True, which='minor', color='#e0e0e0', linestyle=':', linewidth=0.5, alpha=0.7)

    # Sumbu Salib Utama
    ax.axhline(0, color='black', linewidth=1.2)
    ax.axvline(0, color='black', linewidth=1.2)

    # Titik Tangkap Pusat (Titik Lingkaran di 0,0)
    ax.plot(0, 0, marker='o', markersize=8, markerfacecolor='white', markeredgecolor='gray', markeredgewidth=2, zorder=5)

    vx_list = df_calc["Vx (cm)"].values
    vy_list = df_calc["Vy (cm)"].values
    n_gaya = len(df_calc)

    resultant_colors = ['#1a76d2', '#e53935', '#4caf50', '#00bcd4', '#9c27b0']
    all_x = [0.0]
    all_y = [0.0]

    # --- LOGIKA VISUALISASI BERDASARKAN METODE ---
    if metode == "Jajaran Genjang Bertingkat" and n_gaya >= 2:
        # Plot Vektor Asli dari Titik Tangkap Pusat (0,0)
        for idx, row in df_calc.iterrows():
            vx, vy = row["Vx (cm)"], row["Vy (cm)"]
            all_x.append(vx)
            all_y.append(vy)
            ax.quiver(0, 0, vx, vy, angles='xy', scale_units='xy', scale=1, 
                      color='#333333', width=0.005, zorder=4)
            
            offset_x = 0.3 if vx >= 0 else -0.8
            offset_y = 0.3 if vy >= 0 else -0.5
            ax.text(vx + offset_x, vy + offset_y, f"{row['Gaya']}= {row['Beban (kg)']:.0f} Kg", 
                    fontsize=9, fontweight='bold', color='black')

        # Langkah Pertama: R1 dari P1 dan P2
        r_x = vx_list[0] + vx_list[1]
        r_y = vy_list[0] + vy_list[1]
        all_x.append(r_x)
        all_y.append(r_y)

        # Proyeksi P1 dan P2 (Garis Putus-Putus)
        ax.plot([vx_list[0], r_x], [vy_list[0], r_y], linestyle='--', color='#555555', linewidth=1.2)
        ax.plot([vx_list[1], r_x], [vy_list[1], r_y], linestyle='--', color='#555555', linewidth=1.2)

        c_r1 = resultant_colors[0]
        ax.quiver(0, 0, r_x, r_y, angles='xy', scale_units='xy', scale=1, 
                  color=c_r1, width=0.006, label="R1", zorder=3)
        ax.text(r_x * 0.85, r_y * 0.9, "R1", fontsize=10, fontweight='bold', color=c_r1)

        prev_rx, prev_ry = r_x, r_y

        # Langkah Selanjutnya: R2, R3, ..., RAkhir
        for i in range(2, n_gaya):
            px, py = vx_list[i], vy_list[i]
            next_rx = prev_rx + px
            next_ry = prev_ry + py
            
            all_x.append(next_rx)
            all_y.append(next_ry)

            is_last = (i == n_gaya - 1)
            r_name = f"R{i}" if not is_last else "RAkhir"
            r_color = resultant_colors[(i-1) % len(resultant_colors)] if not is_last else '#00acc1'

            proj_color_1 = '#e53935' if i == 3 else ('#555555' if i == 2 else '#4caf50')
            proj_color_2 = '#1a76d2' if i == 2 else ('#555555' if i == 3 else '#1a76d2')

            ax.plot([prev_rx, next_rx], [prev_ry, next_ry], linestyle='--', color=proj_color_1, linewidth=1.3)
            ax.plot([px, next_rx], [py, next_ry], linestyle='--', color=proj_color_2, linewidth=1.3)

            if i == 2:
                ax.plot(px, py, marker='o', markersize=6, markerfacecolor='white', markeredgecolor='gray', markeredgewidth=1.5)

            ax.quiver(0, 0, next_rx, next_ry, angles='xy', scale_units='xy', scale=1, 
                      color=r_color, width=0.007 if not is_last else 0.008, label=r_name, zorder=4)
            ax.text(next_rx * 0.88, next_ry * 0.95, f"{r_name}", fontsize=10, fontweight='bold', color=r_color)

            prev_rx, prev_ry = next_rx, next_ry

    else: # Metode Poligon Gaya (Tip-to-Tail)
        curr_x, curr_y = 0.0, 0.0
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        for idx, row in df_calc.iterrows():
            vx, vy = row["Vx (cm)"], row["Vy (cm)"]
            next_x = curr_x + vx
            next_y = curr_y + vy
            
            all_x.extend([curr_x, next_x])
            all_y.extend([curr_y, next_y])

            ax.quiver(curr_x, curr_y, vx, vy, angles='xy', scale_units='xy', scale=1, 
                      color=colors[idx % len(colors)], width=0.006, label=f"{row['Gaya']}")
            ax.text((curr_x + next_x)/2, (curr_y + next_y)/2, f" {row['Gaya']}", 
                    fontsize=10, fontweight='bold', color=colors[idx % len(colors)])
            
            curr_x, curr_y = next_x, next_y

        end_x, end_y = curr_x, curr_y
        ax.quiver(0, 0, end_x, end_y, angles='xy', scale_units='xy', scale=1, 
                  color='red', width=0.008, label="R Akhir")

    # Formula / Hasil Akhir
    end_x = df_calc["Vx (cm)"].sum()
    end_y = df_calc["Vy (cm)"].sum()
    
    ax.text(0.5, -0.12, f"Rakhir = {R_total_cm:.2f} cm x {skala:.0f} kg = {R_total_kg:.0f} kg", 
            transform=ax.transAxes, ha='center', va='center', fontsize=11, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="black", lw=1))

    # Watermark Penulis di Dalam Gambar Diagram
    fig.text(0.99, 0.01, "Created by : IrwanZanur@MekTek", 
             fontsize=9, color='gray', ha='right', va='bottom', fontstyle='italic', fontweight='bold')

    ax.set_xlabel("Sumbu X (cm)")
    ax.set_ylabel("Sumbu Y (cm)")
    ax.legend(loc="upper left")

    # Batas Sumbu Otomatis
    margin = 3.0
    ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
    ax.set_ylim(min(all_y) - margin, max(all_y) + margin)

    # --- LAYOUT DUA KOLOM (GRAFIK & EXPORT PANEL) ---
    col_plot, col_export = st.columns([3, 1])

    with col_plot:
        st.pyplot(fig)

    with col_export:
        st.subheader("📥 Export Hasil")
        st.write("Unduh hasil kalkulasi dan grafik:")

        buf_png = io.BytesIO()
        fig.savefig(buf_png, format="png", bbox_inches='tight', dpi=300)
        st.download_button(
            label="🖼️ Gambar PNG (HD)",
            data=buf_png.getvalue(),
            file_name=f"diagram_gaya_{metode.lower().replace(' ', '_')}.png",
            mime="image/png"
        )

        buf_pdf = io.BytesIO()
        fig.savefig(buf_pdf, format="pdf", bbox_inches='tight')
        st.download_button(
            label="📄 Vektor PDF",
            data=buf_pdf.getvalue(),
            file_name=f"diagram_gaya_{metode.lower().replace(' ', '_')}.pdf",
            mime="application/pdf"
        )

        csv_data = df_calc[["Gaya", "Beban (kg)", "Panjang (cm)", "Sudut (°)", "Fx (kg)", "Fy (kg)"]].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Tabel CSV",
            data=csv_data,
            file_name="analisis_komponen_gaya.csv",
            mime="text/csv"
        )

    # --- TABEL EKSPANDER RINCIAN ANALITIS ---
    with st.expander("📊 Lihat Detail Perhitungan Komponen Vektor"):
        st.dataframe(
            df_calc[["Gaya", "Beban (kg)", "Panjang (cm)", "Sudut (°)", "Fx (kg)", "Fy (kg)"]],
            use_container_width=True
        )

    # --- PANDUAN & LANGKAH PENGERJAAN STEP-BY-STEP ---
    with st.expander("📖 Panduan & Langkah Pengerjaan Belajar Mandiri (Step-by-Step)", expanded=True):
        st.subheader("1. Konversi Gaya ke Skala Panjang Gambar")
        st.write(f"Skala yang diterapkan: **1 cm = {skala:.0f} kg**")
        
        konversi_text = ""
        for idx, row in df_calc.iterrows():
            konversi_text += f"* **{row['Gaya']}**: {row['Beban (kg)']:.0f} kg ÷ {skala:.0f} kg/cm = **{row['Panjang (cm)']:.2f} cm** (Sudut {row['Sudut (°)']}°)\n"
        st.markdown(konversi_text)
        
        st.subheader("2. Analisis Komponen Gaya (Sumbu X dan Y)")
        st.write("Uraikan setiap gaya ke dalam komponen horizontal ($F_x$) dan vertikal ($F_y$):")
        st.latex(r"F_x = F \cdot \cos(\theta), \quad F_y = F \cdot \sin(\theta)")
        
        komponen_text = ""
        for idx, row in df_calc.iterrows():
            komponen_text += f"* **{row['Gaya']}** ({row['Beban (kg)']:.0f} kg, {row['Sudut (°)']}°):\n"
            komponen_text += f"  * $F_x = {row['Beban (kg)']:.0f} \\cdot \\cos({row['Sudut (°)']}°) = \\mathbf{{{row['Fx (kg)']:.2f}\\text{{ kg}}}}$\n"
            komponen_text += f"  * $F_y = {row['Beban (kg)']:.0f} \\cdot \\sin({row['Sudut (°)']}°) = \\mathbf{{{row['Fy (kg)']:.2f}\\text{{ kg}}}}$\n"
        st.markdown(komponen_text)
        
        st.write("**Total Akumulasi Komponen Gaya:**")
        st.markdown(f"* $\\sum F_x = \\mathbf{{{Rx_kg:.2f}\\text{{ kg}}}}$")
        st.markdown(f"* $\\sum F_y = \\mathbf{{{Ry_kg:.2f}\\text{{ kg}}}}$")
        
        st.subheader("3. Perhitungan Resultan Akhir (Analitis)")
        st.write("Hitung nilai resultan gaya ($R$) dan sudut arahnya ($\theta_R$):")
        st.latex(r"R = \sqrt{(\sum F_x)^2 + (\sum F_y)^2}")
        st.markdown(f"* $R = \\sqrt{{({Rx_kg:.2f})^2 + ({Ry_kg:.2f})^2}} = \\mathbf{{{R_total_kg:.2f}\\text{{ kg}}}}$")
        st.markdown(f"* Panjang garis $R$ pada kertas = ${R_total_kg:.2f} \\text{{ kg}} \\div {skala:.0f} \\text{{ kg/cm}} = \\mathbf{{{R_total_cm:.2f}\\text{{ cm}}}}$")
        
        st.latex(r"\theta_R = \arctan\left(\frac{\sum F_y}{\sum F_x}\right)")
        st.markdown(f"* Sudut Resultan $\\theta_R = \\mathbf{{{Sudut_R_deg:.2f}^\circ}}$")
        
        st.subheader(f"4. Langkah Melukis Diagram Grafis ({metode})")
        if metode == "Jajaran Genjang Bertingkat":
            st.markdown("""
            1. **Tentukan Titik Tangkap**: Buat titik awal $(0,0)$ sebagai pusat seluruh gaya.
            2. **Gambarkan Vektor Asli**: Tarik garis gaya $P_1, P_2, \dots, P_n$ sesuai panjang (cm) dan sudutnya dari titik pusat $(0,0)$.
            3. **Langkah 1 (Jajaran Genjang Pertama)**:
               * Tarik garis proyeksi putus-putus sejajar $P_1$ dari ujung $P_2$.
               * Tarik garis proyeksi putus-putus sejajar $P_2$ dari ujung $P_1$.
               * Titik potong kedua garis proyeksi tersebut adalah ujung **$R_1$**. Tarik garis lurus dari $(0,0)$ ke titik potong tersebut.
            4. **Langkah Bertingkat ($R_2, R_3, \dots, R_{\text{akhir}}$)**:
               * Hubungkan $R_1$ dengan $P_3$ menggunakan garis proyeksi sejajar untuk membentuk **$R_2$**.
               * Lanjutkan proses bertingkat ini secara berurutan hingga gaya terakhir ($P_n$).
            5. **Resultan Akhir**: Garis dari $(0,0)$ menuju titik potong jajaran genjang terakhir adalah **$R_{\text{akhir}}$**.
            """)
        else:
            st.markdown("""
            1. **Tentukan Titik Awal**: Buat titik pusat $(0,0)$ sebagai titik mula menggambar.
            2. **Gambarkan Vektor Pertama ($P_1$)**: Tarik gaya $P_1$ dari titik $(0,0)$ sesuai sudut dan panjang skalanya.
            3. **Gambarkan Vektor Berurutan (Tip-to-Tail)**:
               * Dari **ujung/kepala** $P_1$, tarik garis gaya $P_2$ sesuai sudut dan panjangnya.
               * Dari **ujung/kepala** $P_2$, lanjutkan menarik gaya $P_3$, dan seterusnya hingga gaya terakhir ($P_n$).
            4. **Tarik Resultan Akhir ($R_{\text{akhir}}$)**: Hubungkan garis lurus dari titik awal $(0,0)$ langsung ke **ujung gaya terakhir ($P_n$)**. Garis ini merupakan resultan gaya akhir.
            """)
