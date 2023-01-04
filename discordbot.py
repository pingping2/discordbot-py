from cmath import log
from distutils.sysconfig import PREFIX
import discord
from dotenv import load_dotenv
import os
load_dotenv()

PREFIX = os.environ['PREFIX']
TOKEN = os.environ['TOKEN']

client = discord.Client()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == f'{PREFIX}call':
        await message.channel.send("callback!")

    if message.content.startswith(f'{PREFIX}hello'):
        await message.channel.send('Hello!')


try:
    client.run(TOKEN)
except discord.errors.LoginFailure as e:
    print("Improper token has been passed.")using Discord;
using Discord.WebSocket;
using Google.Cloud.Firestore;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Runtime.Versioning;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;

namespace DiscordBot
{
    class Program
    {
        private readonly DiscordSocketClient _client;
        [SupportedOSPlatform("windows")]
        static void Main()
        {
            new Program().MainAsync().GetAwaiter().GetResult();
        }

        public static string code = string.Empty;
        public static ulong Server_Id, Admin_Id = 1;
        public static string 공지내용 = "공지사항이 없습니다";
        public static string 공지제목 = "공지제목";
        public static ulong buyuser = 0;
        public static bool userisbuying = false;
        string text = string.Empty;
        Product product = new();
        FirestoreDb db;
        [SupportedOSPlatform("windows")]
        public Program()
        {
            var config = new DiscordSocketConfig()
            {
                GatewayIntents = GatewayIntents.All,
                UseInteractionSnowflakeDate = false,
            };

            _client = new DiscordSocketClient(config);
            _client.Log += Log;
            _client.Ready += Ready;
            _client.MessageReceived += MessageReceivedAsync;
            _client.ButtonExecuted += ButtonExecutedAsync;
            _client.SelectMenuExecuted += SelectMenuExecutedAsync;
            _client.ModalSubmitted += ModalSubmittedAsync;
            _client.SlashCommandExecuted += SlashCommandExecutedAsync;
        }
        public async Task ModalSubmittedAsync(SocketModal modal)
        {
            switch (modal.Data.CustomId)
            {
                case "계좌이체":
                    {
                        //await modal.RespondAsync(message, ephemeral: true, components: builder.Build());
                        break;
                    }
                case "핀번호":
                    {
                        List<SocketMessageComponentData> components =
                  modal.Data.Components.ToList();
                        code = components
                            .First(x => x.CustomId == "핀번호").Value;
                        ButtonBuilder 확인 = new()
                        {
                            Label = "확인",
                            CustomId = "확인2",
                            Style = ButtonStyle.Success,
                        };
                        var builder = new ComponentBuilder();
                        builder.WithButton(확인);
                        string message = $"{modal.User.Mention}혹시 정말" + $"{code}(으)로 충전 하실건가요?";

                        await modal.RespondAsync(message, ephemeral: true, components: builder.Build());
                        break;
                    }
                case "수량입력":
                    {
                        List<SocketMessageComponentData> components =
                        modal.Data.Components.ToList();
                        string buynum = (components.First(x => x.CustomId == "수량").Value);
                        int 보유금액 = (int.Parse(Regex.Replace(Information.GetUserData(modal.User.Id.ToString(), db).Result.보유금액, @"[^0-9]", "")) - ((int.Parse(Regex.Replace(product.가격, @"[^0-9]", ""))) * int.Parse(Regex.Replace(buynum, @"[^0-9]", ""))));
                        if (보유금액 < 1)
                        {
                            EmbedBuilder eb = new()
                            {
                                Title = "구매실패",
                                Description = "잔액이 부족합니다",
                                Color = Discord.Color.Blue,
                            };
                            await modal.RespondAsync(embed: eb.Build());
                        }
                        else
                        {
                            Dictionary<string, object> data = new()
                            {
                                {"보유금액", $"`{보유금액}원`" },
                            };
                            Update_Async("Information", modal.User.Id.ToString(), data);
                            switch (text)
                            {
                                case "니트로 생성기":
                                    {
                                        await modal.RespondAsync("https://drive.google.com/file/d/12hopM7gGRR2xBOV7bQ2lJwRi5swTTx2s/view?usp=share_link");
                                        break;
                                    }
                                case "마소 생성기":
                                    {
                                        await modal.RespondAsync("https://drive.google.com/file/d/1j4YTHDcca9vMLte7ovR3v2-tCcLjlebg/view?usp=share_link");
                                        break;
                                    }
                            }
                        }
                        break;
                    }
            }
        }
        public async Task MainAsync()
        {
            string path = AppDomain.CurrentDomain.BaseDirectory + @"\Settings\LUNAR.json";
            Environment.SetEnvironmentVariable("GOOGLE_APPLICATION_CREDENTIALS", path);
            db = FirestoreDb.Create("lunar-shop1");
            await _client.LoginAsync(TokenType.Bot, ReadJson(Environment.CurrentDirectory + @"\Settings\bot_config.json", "TOKEN"));
            await _client.StartAsync();
            Admin_Id = ulong.Parse(ReadJson(Environment.CurrentDirectory + @"\Settings\server_config.json", "Admin_Id"));
            await Task.Delay(-1);
        }
        public async Task<string> GetAllData_Of_A_Document(string Collection, string Document)
        {
            DocumentReference docref = db.Collection(Collection).Document(Document);
            DocumentSnapshot snap = await docref.GetSnapshotAsync();
            string testreturn = string.Empty;
            if (snap.Exists)
            {
                Dictionary<string, object> city = snap.ToDictionary();
                foreach (var item in city)
                {
                    testreturn += string.Format("{0}: {1}\n", item.Key, item.Value);
                }
                return testreturn;
            }
            else
            {
                return string.Empty;
            }
        }

        public async Task<List<KeyValuePair<string, object>>> GetAllData_Of_A_Document_List(string Collection, string Document)
        {
            DocumentReference docref = db.Collection(Collection).Document(Document);
            DocumentSnapshot snap = await docref.GetSnapshotAsync();
            Dictionary<string, object> city = snap.ToDictionary();
            return city.ToList();
        }
        private static string ReadJson(string jsonFilePath, string jsonName)
        {
            using StreamReader file = File.OpenText(jsonFilePath);
            using JsonTextReader reader = new(file);
            JObject json = (JObject)JToken.ReadFrom(reader);
            return json[jsonName].ToString();
        }
        private Task Log(LogMessage log)
        {
            Console.WriteLine(log.ToString());
            return Task.CompletedTask;
        }

        private async Task Ready()
        {
            var 공지 = new SlashCommandBuilder()
             .WithName("공지설정")
             .WithDescription("공지를 설정 할 수 있습니다")
             .AddOption("공지내용", ApplicationCommandOptionType.String, "공지내용을 설정합니다", isRequired: true)
             .AddOption("공지제목", ApplicationCommandOptionType.String, "공지제목을 설정합니다", isRequired: true);
            var 청소 = new SlashCommandBuilder()
           .WithName("청소")
           .WithDescription("메세지를 청소합니다")
           .AddOption("개수", ApplicationCommandOptionType.Integer, "지울 메세지 수를 설정합니다", isRequired: true);
            await _client.CreateGlobalApplicationCommandAsync(공지.Build());
            await _client.CreateGlobalApplicationCommandAsync(청소.Build());
            Console.WriteLine($"{_client.CurrentUser} 연결됨!");
        }
        private async Task SlashCommandExecutedAsync(SocketSlashCommand command)
        {
            switch (command.Data.Name)
            {
                case "공지설정":
                    {
                        if (관리자_권한(command.User.Id))
                        {
                            await 공지설정(command);
                        }
                        else
                        {
                            var embedBuiler = new EmbedBuilder()
                            {
                                Title = "권한부족",
                                Description = "권한이 부족하여 이 명령어를 사용 할 수 없습니다!",
                                Color = Discord.Color.Blue,
                            };
                            await command.RespondAsync(embed: embedBuiler.Build(), ephemeral: true);
                        }

                        break;
                    }
                case "청소":
                    {
                        if (관리자_권한(command.User.Id))
                        {
                            await command.RespondAsync("권한 있음");
                        }
                        else
                        {
                            var embedBuiler = new EmbedBuilder()
                            {
                                Title = "권한부족",
                                Description = "권한이 부족하여 이 명령어를 사용 할 수 없습니다!",
                                Color = Discord.Color.Blue,
                            };
                            await command.RespondAsync(embed: embedBuiler.Build(), ephemeral: true);
                        }
                        break;
                    }

            }
        }
        private bool 관리자_권한(ulong userid)
        {
            bool isadmin = false;
            List<SocketRole> role1 = new();
            foreach (var item in _client.GetGuild(Server_Id).Roles)
            {
                if (item.Permissions.Administrator == true)
                {
                    role1.Add(item);
                }
            }
            foreach (var item in _client.GetGuild(Server_Id).GetUser(userid).Roles)
            {
                if (role1.Contains(item))
                {
                    isadmin = true;
                }
            }
            return isadmin;
        }
        private static async Task 공지설정(SocketSlashCommand command)
        {
            var 공지내용2 = (string)command.Data.Options.ToList()[0].Value;
            var 공지제목2 = (string)command.Data.Options.ToList()[1].Value;
            공지내용 = 공지내용2;
            공지제목 = 공지제목2;
            var embedBuiler = new EmbedBuilder()
            {
                Title = 공지제목2,
                Description = 공지내용2,
                Color = Discord.Color.Blue,
            };
            await command.RespondAsync("공지 미리보기:", embed: embedBuiler.Build(), ephemeral: true);
        }

        public async Task SelectMenuExecutedAsync(SocketMessageComponent arg)
        {
            text = string.Join(", ", arg.Data.Values);
            var products = (await Product.GetAllProduct(db, "Product"));
            buyuser = arg.User.Id;
            foreach (var item in products)
            {
                if (item.이름 == text)
                {
                    product = item; break;
                }
            }
            var mb = new ModalBuilder()
            .WithTitle("수량입력")
            .WithCustomId("수량입력")
            .AddTextInput("수량", "수량", placeholder: "수량을 입력하세요", maxLength: 12);
            await arg.RespondWithModalAsync(mb.Build());

        }
        [SupportedOSPlatform("windows")]
        public async Task ButtonExecutedAsync(SocketMessageComponent component)
        {
            switch (component.Data.CustomId)
            {
                case "확인1":
                    {
                        /*
                         미완성입니다
                         */
                        break;
                    }
                case "확인2":
                    {
                        Thread.Sleep(500);
                        string money = AutoCharge.AutoCheck(code);
                        if(money == "올바르지 않은 문화상품권 코드입니다.")
                        {
                            await component.RespondAsync(money, ephemeral: true);
                        }
                       else
                        {
                            await component.RespondAsync(money, ephemeral: true);
                            string cookie =
                            AutoCharge.AutoChargeCode(cookie, code);
                            int 보유금액 = ((int.Parse(Regex.Replace(Information.GetUserData(component.User.Id.ToString(), db).Result.보유금액, @"[^0-9]", ""))) + int.Parse((Regex.Replace(money, @"[^0-9]", ""))));
                            int 누적금액 = ((int.Parse(Regex.Replace(Information.GetUserData(component.User.Id.ToString(), db).Result.누적금액, @"[^0-9]", ""))) + int.Parse((Regex.Replace(money, @"[^0-9]", ""))));
                            Dictionary<string, object> data = new()
                            {
                                {"보유금액", $"`{보유금액}원`" },
                                { "누적금액", $"`{누적금액}원`" }
                            };
                            Update_Async("Information", component.User.Id.ToString(), data);
                        }

                    

                        break;
                    }
                case "공지":
                    {
                        EmbedBuilder eb = new()
                        {
                            Color = Discord.Color.Blue,
                            Title = 공지제목,
                            Description = 공지내용
                        };
                        await component.RespondAsync(embed: eb.Build(), ephemeral: true);
                        break;
                    }
                case "제품":
                    {
                        EmbedBuilder eb = new()
                        {
                            Color = Discord.Color.Blue,
                            Title = "제품 목록",
                        };
                        List<Product> products = await Product.GetAllProduct(db, "Product");
                        foreach (var item in products)
                        {
                            eb.AddField(item.이름, $"가격: `{item.가격}`\n재고:`{item.재고}`");
                        }
                        await component.RespondAsync(embed: eb.Build(), ephemeral: true);
                        break;
                    }
                case "충전":
                    {
                        EmbedBuilder eb = new()
                        {
                            Color = Discord.Color.Blue,
                            Title = "충전수단 선택",
                            Description = "원하시는 충전수단을 클릭해주세요."
                        };
                        ButtonBuilder 로그인 = new()
                        {
                            Label = "계좌이체",
                            CustomId = "계좌이체",
                            Style = ButtonStyle.Success,
                            IsDisabled = true,
                        };
                        ButtonBuilder 코드 = new()
                        {
                            Label = "코드",
                            CustomId = "코드",
                            Style = ButtonStyle.Primary
                        };
                        var builder = new ComponentBuilder();
                        builder.WithButton(로그인);
                        builder.WithButton(코드);

                        await component.RespondAsync(" ", components: builder.Build(), embed: eb.Build(), ephemeral: true);
                        break;
                    }
                case "정보":
                    {
                        if ((await DocExistBool("Information", component.User.Id.ToString())))
                        {
                            EmbedBuilder eb = new()
                            {
                                Color = Discord.Color.Blue,
                                Title = component.User.Username + "님의 정보",
                                Description = (await GetAllData_Of_A_Document("Information", component.User.Id.ToString())).ToString(),
                            };
                            await component.RespondAsync(ephemeral: true, embed: eb.Build());
                        }
                        else
                        {
                            DocumentReference DOC = db.Collection("Information").Document(component.User.Id.ToString());
                            Dictionary<string, object> data1 = new()
                            {
                                {"경고수", "`0회`" },
                                {"구매수","`0회`" },
                                {"누적금액", "`0원`" },
                                { "보유금액", "`0원`" },
                                { "할인율", "`0%`" }
                            };

                            try
                            {
                                await DOC.SetAsync(data1);
                            }
                            catch (Exception ex)
                            {
                                await component.RespondAsync("오류 발생" + ex.Message + ":" + ex.Data);
                            }
                            EmbedBuilder eb = new()
                            {
                                Color = Discord.Color.Blue,
                                Title = component.User.Username + "님의 정보",
                                Description = (await GetAllData_Of_A_Document("Information", component.User.Id.ToString())).ToString(),
                            };
                            await component.RespondAsync(ephemeral: true, embed: eb.Build());
                        }
                        break;
                    }
                case "구매":
                    {
                        EmbedBuilder eb = new()
                        {
                            Color = Discord.Color.Blue,
                            Title = "제품 선택",
                            Description = "구매할 제품을 선택해주세요."
                        };
                        SelectMenuBuilder selectMenu = new()
                        {
                            CustomId = "구매 메뉴",
                            Placeholder = "구매하기"
                        };
                        List<Product> products = await Product.GetAllProduct(db, "Product");
                        foreach (var item in products)
                        {
                            selectMenu.AddOption(item.이름, item.이름, $"{item.가격} | {item.재고}");
                        }
                        buyuser = component.User.Id;
                        userisbuying = true;
                        ComponentBuilder builder = new();
                        builder.WithSelectMenu(selectMenu);
                        await component.User.SendMessageAsync(" ", embed: eb.Build(), components: builder.Build());
                        break;
                    }
                case "로그인":
                    {
                        var mb = new ModalBuilder()
                        .WithTitle("로그인")
                        .WithCustomId("로그인")
                        .AddTextInput("아이디", "아이디", placeholder: "아이디를 입력하세요", maxLength: 12)
                        .AddTextInput("비밀번호", "비밀번호", placeholder: "비밀번호를 입력하세요", maxLength: 12);

                        await component.RespondWithModalAsync(mb.Build());
                        break;
                    }
                case "코드":
                    {
                        var mb = new ModalBuilder()
                        .WithTitle("핀번호")
                        .WithCustomId("핀번호")
                        .AddTextInput("문상 핀번호", "핀번호", placeholder: "문상 핀번호를 입력하세요", maxLength: 16);
                        await component.RespondWithModalAsync(mb.Build());
                        break;
                    }
            }
        }
        async Task<bool> DocExistBool(string Collection, string Document)
        {
            DocumentReference docRef = db.Collection(Collection).Document(Document);
            DocumentSnapshot snapshot = await docRef.GetSnapshotAsync();
            return snapshot.Exists;
        }
        private static string CommandArg(string command, string message)
        {
            if (message.Length > 6)
            {
                if (message[..command.Length] == command)
                {
                    return message.Replace(command, "");
                }
            }
            return null;
        }
       

        private async void Update_Async(string Collection, string Document, Dictionary<string, object> data)
        {
            DocumentReference docref = db.Collection(Collection).Document(Document);
            DocumentSnapshot snap = await docref.GetSnapshotAsync();
            if (snap.Exists)
            {
                await docref.UpdateAsync(data);
            }
        }
        private async Task MessageReceivedAsync(SocketMessage message)
        {
            if (message.Author.Id == Admin_Id)
            {
                if (message.Content.Length > 6)
                {
                    if (message.Content[..6] == "!db 삭제")
                    {
                        DocumentReference docref = db.Collection(message.Content.Replace("!db 삭제 ", "").Split("|")[0]).Document(message.Content.Replace("!db 삭제", "").Split("|")[1]);
                        await docref.DeleteAsync();
                        await message.Channel.SendMessageAsync("초기화 완료!");
                    }
                }
                if (message.Content.Length > 6)
                {
                    if (message.Content[..6] == "!db 추가")
                    {
                        DocumentReference DOC = db.Collection("Product").Document(message.Content.Replace("!db 추가 ", "").Split("|")[0]);
                        Dictionary<string, object> data1 = new()
                        {
                            {"가격", $"{message.Content.Replace("!db 추가 ", "").Split("|")[1]}원" },
                            {"재고",$"{message.Content.Replace("!db 추가 ", "").Split("|")[2]}개" },
                        };
                        await DOC.SetAsync(data1);

                        await message.Channel.SendMessageAsync($"제품이 추가되었습니다!\n" + "{" + $"\n이름: {message.Content.Replace("!db 추가 ", "").Split("|")[0]}\n가격:{message.Content.Replace("!db 추가 ", "").Split("|")[1]}원\n재고:{message.Content.Replace("!db 추가 ", "").Split("|")[2]}개\n" + "}");
                    }
                }

                if (message.Content == "!커멘드 초기화")
                {
                    try
                    {
                        foreach (var item in await _client.GetGlobalApplicationCommandsAsync())
                        {
                            await item.DeleteAsync();
                        }
                    }
                    catch { }
                    try
                    {
                        foreach (var item in await _client.GetGuild(Server_Id).GetApplicationCommandsAsync())
                        {
                            await item.DeleteAsync();
                        }
                    }
                    catch { }
                    await message.Channel.SendMessageAsync("삭제 성공(봇 제시작 필요)");
                }
                var returnvalue = CommandArg("!수동충전", message.Content);
                if (returnvalue != null)
                {
                    string userid = Regex.Replace(returnvalue.Replace("<@", "").Replace(">", "|").Split("|")[0], @"[^0-9]", "");
                    string price = returnvalue.Replace(">", "|").Split("|")[1].Replace(" ", "");
                    int 보유금액, 누적금액;
                    if (price.FirstOrDefault().ToString() == "-")
                    {
                        보유금액 = (int.Parse(Regex.Replace(Information.GetUserData(userid, db).Result.보유금액, @"[^0-9]", "")) - int.Parse((Regex.Replace(price, @"[^0-9]", ""))));
                        Dictionary<string, object> data = new()
                        {
                            {"보유금액", $"`{보유금액}원`" },
                        };
                        Update_Async("Information", userid, data);
                    }
                    else
                    {
                        보유금액 = ((int.Parse(Regex.Replace(Information.GetUserData(userid, db).Result.보유금액, @"[^0-9]", ""))) + (int.Parse(price)));
                        누적금액 = ((int.Parse(Regex.Replace(Information.GetUserData(userid, db).Result.누적금액, @"[^0-9]", ""))) + (int.Parse(price)));
                        Dictionary<string, object> data = new()
                        {
                            {"보유금액", $"`{보유금액}원`" },
                            { "누적금액", $"`{누적금액}원`" }
                        };
                        Update_Async("Information", userid, data);
                    }
                    await message.Channel.SendMessageAsync(returnvalue.Replace(">", ">님에게") + "원을 수동충전 하였습니다");
                }
                if (message.Content == "!자판기")
                {
                    await message.DeleteAsync();
                    EmbedBuilder eb = new()
                    {
                        Color = Discord.Color.Blue,
                        Title = "LUNAR VENDING",
                        Description = "원하시는 버튼을 클릭해주세요."
                    };
                    ButtonBuilder 공지 = new()
                    {
                        Label = "공지",
                        CustomId = "공지",
                        Style = ButtonStyle.Primary,
                    };
                    ButtonBuilder 제품 = new()
                    {
                        Label = "제품",
                        CustomId = "제품",
                        Style = ButtonStyle.Primary,
                    };
                    ButtonBuilder 충전 = new()
                    {
                        Label = "충전",
                        CustomId = "충전",
                        Style = ButtonStyle.Primary,
                    };
                    ButtonBuilder 정보 = new()
                    {
                        Label = "정보",
                        CustomId = "정보",
                        Style = ButtonStyle.Primary,
                    };
                    ButtonBuilder 구매 = new()
                    {
                        Label = "구매",
                        CustomId = "구매",
                        Style = ButtonStyle.Primary,
                    };
                    var builder = new ComponentBuilder()
                    .WithButton(공지)
                    .WithButton(제품)
                    .WithButton(충전)
                    .WithButton(정보)
                    .WithButton(구매);
                    await message.Channel.SendMessageAsync(" ", components: builder.Build(), embed: eb.Build());
                }
            }
        }
    }
}
