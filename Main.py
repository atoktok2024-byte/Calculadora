from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen, ScreenManager

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

def formatar_molde(valor):
    if valor >= 0:
        return f"-{abs(valor):.2f}"
    else:
        return f"+{abs(valor):.2f}"

# --- Telas da Aplicação Kivy ---

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        
        main_layout.add_widget(Label(text="Calculadora de Curvas", 
                                     font_size='24sp', 
                                     size_hint_y=None, 
                                     height=dp(60), 
                                     bold=True,
                                     color=(0, 0, 0, 1)))
        
        scroll_view = ScrollView()
        input_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10), size_hint_y=None)
        input_layout.bind(minimum_height=input_layout.setter('height'))
        
        text_font_size = '20sp'
        
        self.n_material_input = TextInput(hint_text="Índice de Refração (ex: 1.56)", multiline=False, font_size=text_font_size, size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.n_material_input)
        
        input_layout.add_widget(Label(text="[b]Olho Direito (OD)[/b]", size_hint_y=None, height=dp(40), markup=True, font_size=text_font_size, color=(0,0,0,1)))
        self.dioptria_esferico_od_input = TextInput(hint_text="Dioptria Esférica OD", multiline=False, font_size=text_font_size, size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.dioptria_esferico_od_input)
        
        self.dioptria_cilindro_od_input = TextInput(hint_text="Dioptria Cilíndrica OD (opcional)", multiline=False, font_size=text_font_size, size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.dioptria_cilindro_od_input)
        
        self.curva_externa_od_input = TextInput(hint_text="Base real do Bloco OD", multiline=False, font_size=text_font_size, size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.curva_externa_od_input)
        
        input_layout.add_widget(Label(text="[b]Olho Esquerdo (OE)[/b]", size_hint_y=None, height=dp(40), markup=True, font_size=text_font_size, color=(0,0,0,1)))
        self.dioptria_esferico_oe_input = TextInput(hint_text="Dioptria Esférica OE", multiline=False, font_size=text_font_size, size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.dioptria_esferico_oe_input)
        
        self.dioptria_cilindro_oe_input = TextInput(hint_text="Dioptria Cilíndrica OE (opcional)", multiline=False, font_size=text_font_size, size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.dioptria_cilindro_oe_input)
        
        self.curva_externa_oe_input = TextInput(hint_text="Base real do Bloco OE", multiline=False, font_size=text_font_size, size_hint_y=None, height=dp(50))
        input_layout.add_widget(self.curva_externa_oe_input)
        
        scroll_view.add_widget(input_layout)
        main_layout.add_widget(scroll_view)
        
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(60))
        
        calc_button = Button(text="Calcular", font_size='20sp', bold=True, background_color=(0.3,0.3,0.3,1))
        calc_button.bind(on_press=self.on_calculate_curvas)
        button_layout.add_widget(calc_button)

        history_button = Button(text="Histórico", font_size='20sp', bold=True, background_color=(0.3,0.3,0.3,1))
        history_button.bind(on_press=self.go_to_history)
        button_layout.add_widget(history_button)
        
        main_layout.add_widget(button_layout)
        
        self.error_label = Label(text="", halign='center', valign='top', markup=True, size_hint_y=None, font_size='18sp', color=(1,0,0,1))
        main_layout.add_widget(self.error_label)

        self.add_widget(main_layout)

    def on_calculate_curvas(self, instance):
        self.error_label.text = ""
        
        n_material_text = self.n_material_input.text.replace(',', '.')
        
        if not n_material_text:
            self.error_label.text = "Erro: O campo 'Índice de Refração' é obrigatório."
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
                self.error_label.text = "Erro: Preencha os campos para o Olho Direito (OD) ou Olho Esquerdo (OE)."
                return

            result_data = {
                'n_material': n_material_text,
                'od': None,
                'oe': None
            }
            
            if od_filled:
                dioptria_esferico_od = float(od_esferico_text)
                dioptria_cilindro_od = float(od_cilindro_text) if od_cilindro_text.strip() else 0.0
                curva_externa_od = float(od_curva_text)
                
                esferico_real_od = calcular_dioptria_real(dioptria_esferico_od, n_material)
                
                if abs(dioptria_cilindro_od) < 0.01:
                    curva_interna_od, _ = calcular_curvas_surfacagem(esferico_real_od, None, curva_externa_od)
                    molde_esferico_sugerido_od = sugerir_molde(curva_interna_od)
                    moldes_sugeridos_od = formatar_molde(molde_esferico_sugerido_od)
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
                    moldes_sugeridos_od = f"{formatar_molde(molde_esferico_sugerido_od)} / {formatar_molde(molde_cilindrico_sugerido_od)}"
                
                result_data['od'] = {
                    'esferico': od_esferico_text,
                    'cilindro': od_cilindro_text,
                    'curva_externa': od_curva_text,
                    'molde_sugerido': moldes_sugeridos_od
                }

            if oe_filled:
                dioptria_esferico_oe = float(oe_esferico_text)
                dioptria_cilindro_oe = float(oe_cilindro_text) if oe_cilindro_text.strip() else 0.0
                curva_externa_oe = float(oe_curva_text)
                
                esferico_real_oe = calcular_dioptria_real(dioptria_esferico_oe, n_material)
                
                if abs(dioptria_cilindro_oe) < 0.01:
                    curva_interna_oe, _ = calcular_curvas_surfacagem(esferico_real_oe, None, curva_externa_oe)
                    molde_esferico_sugerido_oe = sugerir_molde(curva_interna_oe)
                    moldes_sugeridos_oe = formatar_molde(molde_esferico_sugerido_oe)
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
                    moldes_sugeridos_oe = f"{formatar_molde(molde_esferico_sugerido_oe)} / {formatar_molde(molde_cilindrico_sugerido_oe)}"
                
                result_data['oe'] = {
                    'esferico': oe_esferico_text,
                    'cilindro': oe_cilindro_text,
                    'curva_externa': oe_curva_text,
                    'molde_sugerido': moldes_sugeridos_oe
                }

            app = App.get_running_app()
            app.add_to_history(result_data)
            
            self.manager.get_screen('result').display_results(result_data)
            self.manager.current = 'result'

        except ValueError:
            self.error_label.text = "Erro: Digite apenas números válidos (ex: -2.00, 1.56). Use ponto ou vírgula para decimais."
        except Exception as e:
            self.error_label.text = f"Ocorreu um erro: {e}"

    def go_to_history(self, instance):
        self.manager.get_screen('history').update_history_display()
        self.manager.current = 'history'

class ResultScreen(Screen):
    def __init__(self, **kwargs):
        super(ResultScreen, self).__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        
        main_layout.add_widget(Label(text="Detalhes do Último Cálculo", 
                                     font_size='24sp', 
                                     size_hint_y=None, 
                                     height=dp(60), 
                                     bold=True,
                                     color=(0, 0, 0, 1)))

        scroll_view = ScrollView()
        self.result_label = Label(text="", halign='left', valign='top', markup=True, size_hint_y=None, font_size='18sp', color=(0,0,0,1))
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        scroll_view.add_widget(self.result_label)
        main_layout.add_widget(scroll_view)
        
        back_button = Button(text="Voltar", size_hint_y=None, height=dp(60), font_size='20sp', bold=True, background_color=(0.3,0.3,0.3,1))
        back_button.bind(on_press=self.go_back)
        main_layout.add_widget(back_button)

        self.add_widget(main_layout)

    def display_results(self, data):
        result_text = "[color=000000][b]Dados do Cálculo:[/b]\n\n"
        
        result_text += f"Índice de Refração: {data['n_material']}\n"
        
        if data['od']:
            od_data = data['od']
            result_text += (f"\n[b]Olho Direito (OD):[/b]\n"
                            f"Dioptria Esférica: {od_data['esferico']}\n"
                            f"Dioptria Cilíndrica: {od_data['cilindro'] if od_data['cilindro'] else '0.0'}\n"
                            f"Base real do Bloco: {od_data['curva_externa']}\n"
                            f"Molde Sugerido: [color=FF0000]{od_data['molde_sugerido']}[/color]\n")
        
        if data['oe']:
            oe_data = data['oe']
            result_text += (f"\n[b]Olho Esquerdo (OE):[/b]\n"
                            f"Dioptria Esférica: {oe_data['esferico']}\n"
                            f"Dioptria Cilíndrica: {oe_data['cilindro'] if oe_data['cilindro'] else '0.0'}\n"
                            f"Base real do Bloco: {oe_data['curva_externa']}\n"
                            f"Molde Sugerido: [color=FF0000]{oe_data['molde_sugerido']}[/color]\n")
        
        self.result_label.text = result_text

    def go_back(self, instance):
        self.manager.current = 'main'

class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))

        main_layout.add_widget(Label(text="Histórico de Cálculos", 
                                     font_size='24sp', 
                                     size_hint_y=None, 
                                     height=dp(60), 
                                     bold=True,
                                     color=(0, 0, 0, 1)))
        
        scroll_view = ScrollView()
        self.history_label = Label(text="", halign='left', valign='top', markup=True, size_hint_y=None, font_size='18sp', color=(0,0,0,1))
        self.history_label.bind(texture_size=self.history_label.setter('size'))
        scroll_view.add_widget(self.history_label)
        main_layout.add_widget(scroll_view)

        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(60))

        back_button = Button(text="Voltar", font_size='20sp', bold=True, background_color=(0.3,0.3,0.3,1))
        back_button.bind(on_press=self.go_back)
        button_layout.add_widget(back_button)

        clear_button = Button(text="Limpar Histórico", font_size='20sp', bold=True, background_color=(0.8,0.2,0.2,1))
        clear_button.bind(on_press=self.clear_history)
        button_layout.add_widget(clear_button)
        
        main_layout.add_widget(button_layout)
        
        self.add_widget(main_layout)

    def update_history_display(self):
        app = App.get_running_app()
        history_string = ""
        if not app.historico_resultados:
            history_string = "Nenhum cálculo no histórico."
        else:
            for i, data in enumerate(reversed(app.historico_resultados)):
                history_string += f"[b]Cálculo {len(app.historico_resultados) - i}:[/b]\n"
                history_string += f"Índice de Refração: {data['n_material']}\n"
                
                if data['od']:
                    od_data = data['od']
                    # Garante que cilindro_od_str seja '0.0' ou um valor numérico válido
                    cilindro_od = od_data['cilindro'].strip()
                    if cilindro_od == '':
                        cilindro_od = '0.0'
                    
                    cilindro_od_str = f"{'-'}{abs(float(cilindro_od))}" if float(cilindro_od) != 0 else ''
                    history_string += (f"  - OD: {od_data['esferico']}{cilindro_od_str} (Base: {od_data['curva_externa']})\n"
                                       f"  - Molde OD: [color=FF0000]{od_data['molde_sugerido']}[/color]\n")
                
                if data['oe']:
                    oe_data = data['oe']
                    # Garante que cilindro_oe_str seja '0.0' ou um valor numérico válido
                    cilindro_oe = oe_data['cilindro'].strip()
                    if cilindro_oe == '':
                        cilindro_oe = '0.0'
                    
                    cilindro_oe_str = f"{'-'}{abs(float(cilindro_oe))}" if float(cilindro_oe) != 0 else ''
                    history_string += (f"  - OE: {oe_data['esferico']}{cilindro_oe_str} (Base: {oe_data['curva_externa']})\n"
                                       f"  - Molde OE: [color=FF0000]{oe_data['molde_sugerido']}[/color]\n")
                
                history_string += "\n"
        
        self.history_label.text = history_string

    def clear_history(self, instance):
        app = App.get_running_app()
        app.historico_resultados = []
        self.update_history_display()

    def go_back(self, instance):
        self.manager.current = 'main'


class CurvasSurfacagemApp(App):
    def build(self):
        self.historico_resultados = []
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ResultScreen(name='result'))
        sm.add_widget(HistoryScreen(name='history'))
        return sm
    
    def add_to_history(self, data):
        self.historico_resultados.append(data)

if __name__ == '__main__':
    CurvasSurfacagemApp().run()
