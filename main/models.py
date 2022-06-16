from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Stmt(models.Model):
    stmt_text = models.CharField(max_length=250)
    stmt_status = models.CharField(max_length=5)
    stmt_date = models.DateField()
    stmt_owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return (self.stmt_text + " Owner: " + self.stmt_owner.username)
    
    def save(self, fact, owner, *args, **kwargs):
        print("ARGUMENTS: ", fact, "Owner: ", owner)
        print("COUNT IS: ", Stmt.objects.filter(stmt_text=fact, stmt_owner=owner).count())
        print(Stmt.objects.filter(stmt_text=fact, stmt_owner=owner))
        count = Stmt.objects.filter(stmt_text=fact, stmt_owner=owner).count()
        if (count != 0):
            print('Statement already exists')
            return False
        else:
            super(Stmt, self).save(*args, **kwargs)

class Review(models.Model):
    claim_text = models.CharField(max_length = 250)
    claim_status = models.CharField(max_length=5)
    claim_reason = models.CharField(max_length = 250)
    claim_submitter = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return (self.claim_text + " Owner: " + self.claim_submitter.username)

    # TODO: save the review
    # def save(self, claim, submitter, *args, **kwargs):
    #     print("ARGUMENTS: ", claim, "Owner: ", submitter)
    #     print("COUNT IS: ", Claims.objects.filter(claim_text=claim, claim_submitter=submitter).count())
    #     print(Claims.objects.filter(claim_text=claim, claim_submitter=submitter))
    #     count = Claims.objects.filter(claim_text=claim, claim_submitter=submitter).count()
    #     if (count != 0):
    #         print('Review already exists')
    #         return False
    #     else:
    #         super(Claims, self).save(*args, **kwargs)
