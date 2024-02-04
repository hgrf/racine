import 'package:flutter/material.dart';

import 'package:requests/requests.dart';
import 'package:html/parser.dart';

import '../sample_feature/sample_item_list_view.dart';

String apiToken = '';

class LoginView extends StatefulWidget {
  const LoginView({super.key});

  @override
  _LoginViewState createState() => _LoginViewState();
}

class _LoginViewState extends State<LoginView> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();

  var _csrfToken = '';

  @override
  Widget build(BuildContext context) {
    Requests.get('http://localhost:5678/auth/login').then((response) {
      final document = parse(response.content());
      final token = document.getElementById("csrf_token")?.attributes['value'];
      _csrfToken = token ?? '';
      // final cookies = CookieJar.parseCookiesString(response.headers['set-cookie'] ?? '');
      // _session = cookies['session']?.value ?? '';
    });
    return Scaffold(
      appBar: AppBar(
        title: const Text('Login'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: <Widget>[
              TextFormField(
                controller: _usernameController,
                decoration: const InputDecoration(labelText: 'Username'),
              ),
              TextFormField(
                controller: _passwordController,
                decoration: const InputDecoration(labelText: 'Password'),
                obscureText: true,
              ),
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 16.0),
                child: ElevatedButton(
                  onPressed: () async {
                    /* NOTE: no need to add cookie manual, the package will handle it */
                    Requests.post('http://localhost:5678/auth/login',
                    json: {
                      'username': _usernameController.text,
                      'password': _passwordController.text,
                      'submit': 'Log+In',
                      'csrf_token': _csrfToken,
                    }).then((value) {
                      if (value.statusCode == 302) {
                        /* we have logged in, now let's load some page (doesn't really matter
                         * which one, as long as it initiates Racine)
                         */
                        Requests.get('http://localhost:5678/profile/overview').then((value) {
                          final i = value.content().indexOf('R.init("');
                          final j = value.content().indexOf('"', i + 8);
                          apiToken = value.content().substring(i + 8, j);
                          Navigator.pushNamed(context, SampleItemListView.routeName);
                        });
                      }
                    });
                  },
                  child: const Text('Login'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
