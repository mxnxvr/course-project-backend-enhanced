// Unity C# example for Register, Login (get token), and request player data.
// Use UnityWebRequest to POST to /api/register/ and /api/login/ then include
// Authorization: Bearer <access_token> for protected endpoints.

// Register example:
// POST /api/register/ body: {username, email, password}

// Login example:
// POST /api/login/ body: {username, password}
// Response contains access and refresh tokens:
// { "access": "...", "refresh": "..." }

// Unity fetch example:
/*
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class ApiExample : MonoBehaviour
{
    IEnumerator Login(string username, string password)
    {
        string url = "https://yourdomain.com/api/login/";
        WWWForm form = new WWWForm();
        form.AddField("username", username);
        form.AddField("password", password);
        using (UnityWebRequest www = UnityWebRequest.Post(url, form))
        {
            yield return www.SendWebRequest();
            if (www.result == UnityWebRequest.Result.Success)
            {
                Debug.Log(www.downloadHandler.text);
                // Parse JSON, store access token, use in later requests
            }
            else
            {
                Debug.LogError(www.error);
            }
        }
    }
}
*/
