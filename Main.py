from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.metrics import dp

# Definir a cor de fundo da janela
Window.clearcolor = (0.95, 0.95, 0.95, 1)

# --- Funções de Cálculo ---

N_FERRAMENTA_LAB = 1.530
N_FERRAMENTA_MINUS_1 = N_FERRAMENTA_LAB - 1

def calcular_dioptria_real(dioptria, n_material):
    if dioptria is None or n_material <= 1: return 0
    n_material_minus_1 = n_material - 1
    return dioptria * (N_FERRAMENTA_MINUS_1 / n_material_minus_1)

def calcular_curvas_surfacagem(dioptria_esferico_real, dioptria_cilindro_real, curva_externa):
    curva_interna = curva_externa - dioptria_esferico_real
    curva_cilindro = None
    if dioptria_cilindro_real is not None:
        curva_cilindro = curva_interna + abs(dioptria_cilindro_real)
    return curva_interna, curva_cilindro

def sugerir_molde(curva):
    curva_positiva = abs(curva)
    molde_candidato = 12.0
    soma_atual = 13
    if curva_positiva < 12.0: return 12.0
    while True:
        proximo_molde = molde_candidato + soma_atual
        if abs(curva_positiva - proximo_molde) > abs(curva_positiva - molde_candidato):
            if abs(curva_positiva - molde_candidato) < abs(curva_positiva - proximo_molde):
                valor_sugerido = molde_candidato
            else:
                valor_sugerido = proximo_molde
            break
        molde_candidato = proximo_molde
        if soma_atual == 13: soma_atual = 12
        else: soma_atual = 13
    if curva < 0: return -valor_sugerido
    else: return valor_sugerido


# --- Classe da Aplicação Kivy ---

class CurvasSurfacagemApp(App):
    def build(self):
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        
        # Título
        main_layout.add_widget(Label(text="Calculadora de Curvas", 
                                     font_size='24sp', 
                                     size_hint_y=None, 
                                     height=dp(60), 
                                     bold=True,
                                     color=(0, 0, 0, 1)))
        
        # Layout de entrada de dados dentro de um ScrollView
        scroll_view = ScrollView()
        input_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10), size_hint_y=None)
        input_layout.bind(minimum_height=input_layout.setter('height'))
        
        text_font_size = '20sp'
        
        self.n_material_input = TextInput(hint_text="Índice de Refração (ex: 1.56)", multiline=False, font_size=text_font_size, size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.n_material_input)
        
        # OD
        input_layout.add_widget(Label(text="[b]Olho Direito (OD)[/b]", size_hint_y=None, height=dp(40), markup=True, font_size=text_font_size, color=(0,0,0,1)))
        self.dioptria_esferico_od_input = TextInput(hint_text="Dioptria Esférica OD", multiline=False, font_size=text_font_size, size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.dioptria_esferico_od_input)
        
        self.dioptria_cilindro_od_input = TextInput(hint_text="Dioptria Cilíndrica OD (opcional)", multiline=False, font_size=text_font_size, size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.dioptria_cilindro_od_input)
        
        self.curva_externa_od_input = TextInput(hint_text="Base real do Bloco OD", multiline=False, font_size=text_font_size, size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.curva_externa_od_input)
        
        # OE
        input_layout.add_widget(Label(text="[b]Olho Esquerdo (OE)[/b]", size_hint_y=None, height=dp(40), markup=True, font_size=text_font_size, color=(0,0,0,1)))
        self.dioptria_esferico_oe_input = TextInput(hint_text="Dioptria Esférica OE", multiline=False, font_size=text_font_size, size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.dioptria_esferico_oe_input)
        
        self.dioptria_cilindro_oe_input = TextInput(hint_text="Dioptria Cilíndrica OE (opcional)", multiline=False, font_size=text_font_size, size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.dioptria_cilindro_oe_input)
        
        self.curva_externa_oe_input = TextInput(hint_text="Base real do Bloco OE", multiline=False, font_size=text_font_size, size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.curva_externa_oe_input)
        
        scroll_view.add_widget(input_layout)
        main_layout.add_widget(scroll_view)
        
        # Botão de cálculo
        calc_button = Button(text="Calcular", size_hint_y=None, height=dp(60), font_size='20sp', bold=True, background_color=(0.3,0.3,0.3,1))
        calc_button.bind(on_press=self.on_calculate_curvas)
        main_layout.add_widget(calc_button)
        
        # Label de resultado
        self.result_label = Label(text="", halign='left', valign='top', markup=True, size_hint_y=None, font_size='18sp', color=(0,0,0,1))
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        main_layout.add_widget(self.result_label)
        
        return main_layout

    def on_calculate_curvas(self, instance):
        n_material_text = self.n_material_input.text.replace(',', '.')
        
        if not n_material_text:
            self.result_label.text = "[color=FF0000]Erro: O campo 'Índice de Refração' é obrigatório.[/color]"
            return

        try:
            n_material = float(n_material_text)
            
            od_esferico_text = self.dioptria_esferico_od_input.text.replace(',', '.')
            od_cilindro_text = self.dioptria_cilindro_od_input.text.replace(',', '.')
            od_curva_text = self.curva_externa_od_input.text.replace(',', '.')
            
            oe_esferico_text = self.dioptria_esferico_oe_input.text.replace(',', '.')
            oe_cilindro_text = self.dioptria_cilindro_oe_input.text.replace(',', '.')
            oe_curva_text = self.curva_externa_oe_input.text.replace(',', '.')
            
            od_filled = od_esferico_text.strip() and od_curva_text.strip()
            oe_filled = oe_esferico_text.strip() and oe_curva_text.strip()
            
            if not od_filled and not oe_filled:
                self.result_label.text = "[color=FF0000]Erro: Preencha os campos para o Olho Direito (OD) ou Olho Esquerdo (OE).[/color]"
                return

            result_text = "[color=000000]Resultados:\n\n" 
            
            if od_filled:
                dioptria_esferico_od = float(od_esferico_text)
                dioptria_cilindro_od = float(od_cilindro_text) if od_cilindro_text.strip() else 0.0
                curva_externa_od = float(od_curva_text)
                
                esferico_real_od = calcular_dioptria_real(dioptria_esferico_od, n_material)
                
                # Verifica se o cilindro é zero antes de fazer os cálculos e exibir
                if abs(dioptria_cilindro_od) < 0.01:
                    curva_interna_od, _ = calcular_curvas_surfacagem(esferico_real_od, None, curva_externa_od)
                    molde_esferico_sugerido_od = sugerir_molde(curva_interna_od)
                    moldes_sugeridos_od = f"{molde_esferico_sugerido_od:.2f}"
                else:
                    cilindro_real_od = calcular_dioptria_real(dioptria_cilindro_od, n_material)
                    curva_interna_od, curva_cilindro_od = calcular_curvas_surfacagem(esferico_real_od, cilindro_real_od, curva_externa_od)
                    
                    molde_esferico_sugerido_od = sugerir_molde(curva_interna_od)
                    compensacao_od = molde_esferico_sugerido_od - curva_interna_od
                    
                    if molde_esferico_sugerido_od < 0:
                        curva_cilindro_compensada_od = curva_interna_od - abs(cilindro_real_od) + compensacao_od
                    else:
                        curva_cilindro_compensada_od = curva_cilindro_od + compensacao_od
                    
                    molde_cilindrico_sugerido_od = sugerir_molde(curva_cilindro_compensada_od) if curva_cilindro_compensada_od is not None else None
                    moldes_sugeridos_od = f"{molde_esferico_sugerido_od:.2f} / {molde_cilindrico_sugerido_od:.2f}"
                
                result_text += (f"OD:\n"
                                f"Molde Sugerido: {moldes_sugeridos_od}\n\n")

            if oe_filled:
                dioptria_esferico_oe = float(oe_esferico_text)
                dioptria_cilindro_oe = float(oe_cilindro_text) if oe_cilindro_text.strip() else 0.0
                curva_externa_oe = float(oe_curva_text)
                
                esferico_real_oe = calcular_dioptria_real(dioptria_esferico_oe, n_material)
                
                if abs(dioptria_cilindro_oe) < 0.01:
                    curva_interna_oe, _ = calcular_curvas_surfacagem(esferico_real_oe, None, curva_externa_oe)
                    molde_esferico_sugerido_oe = sugerir_molde(curva_interna_oe)
                    moldes_sugeridos_oe = f"{molde_esferico_sugerido_oe:.2f}"
                else:
                    cilindro_real_oe = calcular_dioptria_real(dioptria_cilindro_oe, n_material)
                    curva_interna_oe, curva_cilindro_oe = calcular_curvas_surfacagem(esferico_real_oe, cilindro_real_oe, curva_externa_oe)
                    
                    molde_esferico_sugerido_oe = sugerir_molde(curva_interna_oe)
                    compensacao_oe = molde_esferico_sugerido_oe - curva_interna_oe
                    
                    if molde_esferico_sugerido_oe < 0:
                        curva_cilindro_compensada_oe = curva_interna_oe - abs(cilindro_real_oe) + compensacao_oe
                    else:
                        curva_cilindro_compensada_oe = curva_cilindro_oe + compensacao_oe
                    
                    molde_cilindrico_sugerido_oe = sugerir_molde(curva_cilindro_compensada_oe) if curva_cilindro_compensada_oe is not None else None
                    moldes_sugeridos_oe = f"{molde_esferico_sugerido_oe:.2f} / {molde_cilindrico_sugerido_oe:.2f}"
                
                result_text += (f"OE:\n"
                                f"Molde Sugerido: {moldes_sugeridos_oe}\n\n")
            
            result_text += "[/color]"
            self.result_label.text = result_text

        except ValueError:
            self.result_label.text = "[color=FF0000]Erro: Digite apenas números válidos (ex: -2.00, 1.56). Use ponto ou vírgula para decimais.[/color]"
        except Exception as e:
            self.result_label.text = f"[color=FF0000]Ocorreu um erro: {e}[/color]"

if __name__ == '__main__':
    CurvasSurfacagemApp().run()

Adicionando o código da calculadora
